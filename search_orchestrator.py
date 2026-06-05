import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Mapping

import pandas as pd

from exceptions import BrowserSessionError, RobotChallengeError, SearchEngineError, SynthesixError
from scoring import build_relevance_scorer, calculate_relevance
from settings import AppSettings, get_settings
from utils import add_to_history, generate_history_html, generate_html_report


logger = logging.getLogger(__name__)

REQUIRED_RESULT_COLUMNS = ("title", "link", "description", "source")


@dataclass(frozen=True)
class SearchRunResult:
    output_path: str | None
    nb_results: int
    total_time: float
    engine_errors: dict[str, Exception] = field(default_factory=dict)


def _create_google_engine():
    from google import GoogleSearchEngine

    return GoogleSearchEngine()


def _create_bing_engine():
    from bing import BingSearchEngine

    return BingSearchEngine()


def _create_brave_engine():
    from brave import BraveSearchEngine

    return BraveSearchEngine()


def _create_duckduckgo_engine():
    from duckduckgo import DuckDuckGoSearchEngine

    return DuckDuckGoSearchEngine()


DEFAULT_ENGINE_FACTORIES: dict[str, Callable[[], object]] = {
    "google": _create_google_engine,
    "bing": _create_bing_engine,
    "brave": _create_brave_engine,
    "duckduckgo": _create_duckduckgo_engine,
}


def aggregate_search_results(
    engine_results: Mapping[str, pd.DataFrame],
    parsed_query: str,
    scorer: Callable[[dict, str], float] = calculate_relevance,
) -> pd.DataFrame:
    frames = []
    required_column_set = set(REQUIRED_RESULT_COLUMNS)

    for engine, df in engine_results.items():
        if not isinstance(df, pd.DataFrame):
            logger.warning("%s results ignored; expected DataFrame, got %s", engine, type(df).__name__)
            continue
        if df.empty:
            continue
        missing_columns = required_column_set - set(df.columns)
        if missing_columns:
            logger.warning("%s results ignored; missing columns: %s", engine, sorted(missing_columns))
            continue
        frames.append(df)

    if not frames:
        return pd.DataFrame(columns=[*REQUIRED_RESULT_COLUMNS, "relevance_score"])

    combined_df = pd.concat(frames, ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=list(REQUIRED_RESULT_COLUMNS))
    row_scorer = build_relevance_scorer(parsed_query) if scorer is calculate_relevance else (
        lambda row: scorer(row, parsed_query)
    )
    combined_df["relevance_score"] = combined_df.apply(row_scorer, axis=1)
    combined_df = combined_df.sort_values("relevance_score", ascending=False)

    best_idx = combined_df.groupby("link")["relevance_score"].idxmax()
    best_rows = combined_df.loc[best_idx, ["link", "title", "description", "relevance_score"]]
    sources = combined_df.groupby("link")["source"].apply(
        lambda values: ", ".join(sorted(values.astype(str).unique()))
    )

    return (
        best_rows
        .merge(sources.rename("source"), on="link", how="left")
        .sort_values("relevance_score", ascending=False)
    )


class SearchOrchestrator:
    def __init__(
        self,
        engine_factories: Mapping[str, Callable[[], object]] | None = None,
        report_generator: Callable[[pd.DataFrame, str, float, int], str | None] = generate_html_report,
        history_adder: Callable[[str, str, int, str], None] = add_to_history,
        history_report_generator: Callable[[], str] = generate_history_html,
        scorer: Callable[[dict, str], float] = calculate_relevance,
        settings: AppSettings | None = None,
    ):
        self.engine_factories = dict(engine_factories or DEFAULT_ENGINE_FACTORIES)
        self.report_generator = report_generator
        self.history_adder = history_adder
        self.history_report_generator = history_report_generator
        self.scorer = scorer
        self.settings = settings or get_settings()

    async def search(
        self,
        original_query: str,
        parsed_query: str,
        browser,
        engines: Mapping[str, bool],
        num_results: int,
    ) -> SearchRunResult:
        logger.info("Search in progress for: %s", parsed_query)
        start_time = time.monotonic()

        engine_results, engine_errors, attempted_count = await self._run_engines(
            parsed_query,
            browser,
            engines,
            num_results,
        )
        total_time = time.monotonic() - start_time
        logger.info("Global execution time: %.2f seconds", total_time)

        if attempted_count and len(engine_errors) == attempted_count:
            if attempted_count == 1:
                raise next(iter(engine_errors.values()))
            raise SearchEngineError(
                "all",
                "All selected search engines failed.",
                query=parsed_query,
                engine_errors=engine_errors,
            )

        combined_df = aggregate_search_results(engine_results, parsed_query, scorer=self.scorer)
        relevant_results = combined_df[combined_df["relevance_score"] > 0]
        nb_results = len(relevant_results)

        output_path = self.report_generator(relevant_results, parsed_query, total_time, nb_results)
        if output_path:
            logger.info("Generated report: %s", output_path)
            self.history_adder(original_query, parsed_query, nb_results, output_path)
            self.history_report_generator()
        else:
            logger.error("Can't generate report.")

        return SearchRunResult(
            output_path=output_path,
            nb_results=nb_results,
            total_time=total_time,
            engine_errors=engine_errors,
        )

    async def _run_engines(
        self,
        parsed_query: str,
        browser,
        selected_engines: Mapping[str, bool],
        num_results: int,
    ) -> tuple[dict[str, pd.DataFrame], dict[str, Exception], int]:
        tasks = []
        concurrency = max(1, self.settings.engine_concurrency)
        semaphore = asyncio.Semaphore(concurrency)
        for engine_name, enabled in selected_engines.items():
            if not enabled:
                continue

            factory = self.engine_factories.get(engine_name)
            if factory is None:
                logger.warning("Unknown search engine selected: %s", engine_name)
                continue

            engine = factory()
            tasks.append((
                engine_name,
                asyncio.create_task(self._search_engine_limited(
                    semaphore,
                    engine_name,
                    engine,
                    parsed_query,
                    browser,
                    num_results,
                )),
            ))

        if not tasks:
            logger.warning("No search engine selected.")
            return {}, {}, 0

        results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
        engine_results = {}
        engine_errors = {}

        for (engine_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                error = self._normalize_engine_error(engine_name, result)
                logger.error(
                    "%s search failed: %s",
                    engine_name,
                    error,
                    exc_info=(type(result), result, result.__traceback__),
                )
                engine_errors[engine_name] = error
                engine_results[engine_name] = pd.DataFrame()
            else:
                engine_results[engine_name] = result

        return engine_results, engine_errors, len(tasks)

    async def _search_engine_limited(
        self,
        semaphore: asyncio.Semaphore,
        engine_name: str,
        engine,
        parsed_query: str,
        browser,
        num_results: int,
    ) -> pd.DataFrame:
        async with semaphore:
            return await self._search_engine_with_retries(
                engine_name,
                engine,
                parsed_query,
                browser,
                num_results,
            )

    def _normalize_engine_error(self, engine_name: str, error: Exception) -> Exception:
        if isinstance(error, SynthesixError):
            return error
        return SearchEngineError(
            engine_name,
            f"{engine_name} search failed.",
            original_error=error,
        )

    async def _search_engine_with_retries(
        self,
        engine_name: str,
        engine,
        parsed_query: str,
        browser,
        num_results: int,
    ) -> pd.DataFrame:
        attempts = max(0, self.settings.engine_retry_attempts)
        delay = max(0.0, self.settings.engine_retry_delay)
        backoff = max(1.0, self.settings.engine_retry_backoff)
        last_error = None

        for attempt_index in range(attempts + 1):
            try:
                return await asyncio.wait_for(
                    engine.search(parsed_query, browser, num_results),
                    timeout=self.settings.engine_search_timeout,
                )
            except Exception as exc:
                error = self._normalize_engine_error(engine_name, exc)
                last_error = error
                if attempt_index >= attempts or not self._is_retryable_error(error):
                    raise error from exc

                logger.warning(
                    "%s search failed with a retryable error; retrying in %.2fs (%s/%s): %s",
                    engine_name,
                    delay,
                    attempt_index + 1,
                    attempts,
                    error,
                )
                if delay > 0:
                    await asyncio.sleep(delay)
                delay *= backoff

        raise last_error

    def _is_retryable_error(self, error: Exception) -> bool:
        if isinstance(error, RobotChallengeError):
            return False
        if isinstance(error, BrowserSessionError):
            return True
        if isinstance(error, TimeoutError):
            return True
        if isinstance(error, SearchEngineError):
            if isinstance(error.original_error, (TimeoutError, ConnectionError, OSError)):
                return True
            message = str(error).lower()
            return "timeout" in message or "did not load" in message
        return isinstance(error, (ConnectionError, OSError))
