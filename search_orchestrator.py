import asyncio
import logging
import time
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Mapping

from exceptions import BrowserSessionError, RobotChallengeError, SearchEngineError, SynthesixError
from query_operators import SearchFilters, build_engine_query, result_matches_filters
from search_engine import EngineTabPool
from scoring import (
    ScoreBreakdown,
    ScoreComponent,
    add_context_to_breakdown,
    build_relevance_explainer,
    calculate_relevance,
)
from settings import AppSettings, get_settings
from utils import add_to_history, generate_history_html, generate_html_report


logger = logging.getLogger(__name__)

REQUIRED_RESULT_COLUMNS = ("title", "link", "description", "source")


class SearchResults(list[dict]):
    """Result rows with the small metadata payload needed by report rendering."""

    def __init__(self, rows: Iterable[Mapping] = (), *, attrs: Mapping | None = None) -> None:
        super().__init__(dict(row) for row in rows)
        self.attrs = dict(attrs or {})

    def copy(self) -> "SearchResults":
        return type(self)(self, attrs=self.attrs)


@dataclass(frozen=True)
class SearchRunResult:
    output_path: str | None
    nb_results: int
    total_time: float
    engine_errors: dict[str, Exception] = field(default_factory=dict)
    results: tuple[dict, ...] = ()
    coverage: tuple[dict, ...] = ()


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
    engine_results: Mapping[str, list[dict]],
    parsed_query: str,
    scorer: Callable[[dict, str], float] = calculate_relevance,
    filters: SearchFilters | Mapping | None = None,
    base_query: str | None = None,
) -> SearchResults:
    rows: list[dict] = []
    required_column_set = set(REQUIRED_RESULT_COLUMNS)

    for engine, engine_rows in engine_results.items():
        if not isinstance(engine_rows, list):
            logger.warning("%s results ignored; expected list, got %s", engine, type(engine_rows).__name__)
            continue
        if not engine_rows:
            continue
        if not all(isinstance(row, Mapping) for row in engine_rows):
            logger.warning("%s results ignored; every result must be a mapping", engine)
            continue
        available_columns = set().union(*(row.keys() for row in engine_rows))
        missing_columns = required_column_set - available_columns
        if missing_columns:
            logger.warning("%s results ignored; missing columns: %s", engine, sorted(missing_columns))
            continue
        for source_row in engine_rows:
            row = dict(source_row)
            row.setdefault("_engine", str(engine))
            row.setdefault(
                "_query_variant",
                base_query if base_query is not None else parsed_query,
            )
            rows.append(row)

    if not rows:
        return SearchResults()

    deduplicated_rows = []
    seen_rows = set()
    for row in rows:
        duplicate_key = tuple(
            row.get(column)
            for column in (*REQUIRED_RESULT_COLUMNS, "_engine", "_query_variant")
        )
        if duplicate_key in seen_rows:
            continue
        seen_rows.add(duplicate_key)
        deduplicated_rows.append(row)

    filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
    if filters.has_filters():
        deduplicated_rows = [
            row for row in deduplicated_rows if result_matches_filters(row, filters)
        ]
        if not deduplicated_rows:
            return SearchResults()

    if scorer is calculate_relevance:
        explainers = {
            query: build_relevance_explainer(query)
            for query in {str(row["_query_variant"]) for row in deduplicated_rows}
        }
        for row in deduplicated_rows:
            row["_base_breakdown"] = explainers[str(row["_query_variant"])](row)
    else:
        for row in deduplicated_rows:
            row["_base_breakdown"] = ScoreBreakdown((
                ScoreComponent(
                    "custom_score",
                    "Custom relevance score",
                    float(scorer(row, str(row["_query_variant"]))),
                ),
            ))
    for row in deduplicated_rows:
        row["_base_score"] = row["_base_breakdown"].total

    rows_by_link: dict[object, list[dict]] = {}
    for row in deduplicated_rows:
        rows_by_link.setdefault(row["link"], []).append(row)

    filters_matched = filters.has_filters()
    results = SearchResults()
    for link in sorted(rows_by_link, key=str):
        link_rows = rows_by_link[link]
        best_row = max(link_rows, key=lambda row: row["_base_score"])
        engine_count = len({str(row["_engine"]) for row in link_rows})
        score_breakdown = add_context_to_breakdown(
            best_row["_base_breakdown"],
            engine_count=engine_count,
            filters_matched=filters_matched,
        ).to_payload()
        results.append({
            "link": link,
            "title": best_row["title"],
            "description": best_row["description"],
            "engine_count": engine_count,
            "score_breakdown": score_breakdown,
            "relevance_score": sum(float(component["score"]) for component in score_breakdown),
            "query_variants": sorted({str(row["_query_variant"]) for row in link_rows}),
            "source": ", ".join(sorted({str(row["source"]) for row in link_rows})),
        })

    return SearchResults(sorted(results, key=lambda row: -row["relevance_score"]))


class SearchOrchestrator:
    def __init__(
        self,
        engine_factories: Mapping[str, Callable[[], object]] | None = None,
        report_generator: Callable[[SearchResults, str, float, int], str | None] = generate_html_report,
        history_adder: Callable[..., None] = add_to_history,
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
        filters: SearchFilters | Mapping | None = None,
        base_query: str | None = None,
        investigation_id: str | None = None,
        query_variants: Iterable[str] | None = None,
    ) -> SearchRunResult:
        result = await self.collect(
            original_query, parsed_query, browser, engines, num_results,
            filters, base_query, query_variants,
        )
        filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
        relevant_results = SearchResults(result.results, attrs={
            "query_coverage": result.coverage,
            "search_context": {
                "original_query": original_query,
                "filters": filters.to_payload(),
                "num_results": int(num_results),
                "investigation_id": investigation_id or "",
            },
        })
        output_path = self.report_generator(relevant_results, parsed_query, result.total_time, result.nb_results)
        if output_path:
            args = [original_query, parsed_query, result.nb_results, output_path]
            if filters.has_filters():
                args.append(filters.to_payload())
            kwargs = {"investigation_id": investigation_id} if investigation_id else {}
            self.history_adder(*args, **kwargs)
            self.history_report_generator()
        return SearchRunResult(output_path, result.nb_results, result.total_time, result.engine_errors, result.results, result.coverage)

    async def collect(
        self,
        original_query: str,
        parsed_query: str,
        browser,
        engines: Mapping[str, bool],
        num_results: int,
        filters: SearchFilters | Mapping | None = None,
        base_query: str | None = None,
        query_variants: Iterable[str] | None = None,
        on_progress: Callable[[SearchResults, tuple[dict, ...]], Awaitable[None]] | None = None,
    ) -> SearchRunResult:
        """Collect results without rendering reports or writing history."""
        filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
        logger.info("Search in progress for: %s", parsed_query)
        start_time = time.monotonic()
        engine_base_query = base_query if base_query is not None else parsed_query

        execution_queries = tuple(query_variants or ())
        if not execution_queries:
            execution_queries = (engine_base_query,)
        engine_results, engine_errors, attempted_count, coverage = await self._run_engines(
            engine_base_query,
            browser,
            engines,
            num_results,
            filters,
            query_variants=execution_queries,
            on_progress=on_progress,
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

        combined_results = aggregate_search_results(
            engine_results,
            parsed_query,
            scorer=self.scorer,
            filters=filters,
            base_query=base_query,
        )
        relevant_results = SearchResults(
            row for row in combined_results if row["relevance_score"] > 0
        )
        nb_results = len(relevant_results)
        return SearchRunResult(
            output_path=None,
            nb_results=nb_results,
            total_time=total_time,
            engine_errors=engine_errors,
            results=tuple(relevant_results),
            coverage=coverage,
        )

    async def _run_engines(
        self,
        parsed_query: str,
        browser,
        selected_engines: Mapping[str, bool],
        num_results: int,
        filters: SearchFilters,
        query_variants: Iterable[str] | None = None,
        on_progress: Callable[[SearchResults, tuple[dict, ...]], Awaitable[None]] | None = None,
    ) -> tuple[dict[str, list[dict]], dict[str, Exception], int, tuple[dict, ...]]:
        concurrency = max(1, self.settings.engine_concurrency)
        semaphore = asyncio.Semaphore(concurrency)
        queries = tuple(query_variants or (parsed_query,))
        coverage = {
            query: {"query": query, "engines": {}}
            for query in queries
        }
        multiple_queries = len(queries) > 1

        def task_key_for(engine_name: str, query_index: int) -> str:
            return (
                f"{engine_name} [variant {query_index + 1}]"
                if multiple_queries
                else engine_name
            )

        # T-014: one tab per engine for the whole run, one asyncio task per
        # engine — variants are successive navigations of the same tab, so a
        # multi-variant search no longer churns one tab per (engine, variant).
        pool = EngineTabPool(browser)
        engines: list[tuple[str, object]] = []
        for engine_name, enabled in selected_engines.items():
            if not enabled:
                continue
            factory = self.engine_factories.get(engine_name)
            if factory is None:
                logger.warning("Unknown search engine selected: %s", engine_name)
                continue
            engine = factory()
            engine.search_filters = filters
            engine.tab_pool = pool
            engines.append((engine_name, engine))

        if not engines:
            logger.warning("No search engine selected.")
            return {}, {}, 0, ()

        engine_results: dict[str, list[dict]] = {}
        engine_errors: dict[str, Exception] = {}

        async def run_engine(engine_name: str, engine) -> None:
            # Per-variant bookkeeping lives inside the task so everything
            # finished before the T-010 deadline stays recorded.
            for query_index, query in enumerate(queries):
                task_key = task_key_for(engine_name, query_index)
                engine_query = build_engine_query(query, engine_name, filters)
                try:
                    result = await self._search_engine_limited(
                        semaphore,
                        engine_name,
                        engine,
                        engine_query,
                        browser,
                        num_results,
                    )
                except Exception as exc:
                    error = self._normalize_engine_error(engine_name, exc)
                    logger.error(
                        "%s search failed: %s",
                        engine_name,
                        error,
                        exc_info=(type(exc), exc, exc.__traceback__),
                    )
                    engine_errors[task_key] = error
                    engine_results[task_key] = []
                    coverage[query]["engines"][engine_name] = {
                        "status": self._coverage_error_status(error),
                        "count": 0,
                    }
                else:
                    result_rows = [dict(row) for row in result]
                    for row in result_rows:
                        row["_engine"] = engine_name
                        row["_query_variant"] = query
                    engine_results[task_key] = result_rows
                    coverage[query]["engines"][engine_name] = {
                        "status": "ok",
                        "count": len(result_rows),
                    }
                if on_progress is not None:
                    rows = aggregate_search_results(engine_results, parsed_query, self.scorer, filters)
                    try:
                        await on_progress(SearchResults(row for row in rows if row["relevance_score"] > 0), deepcopy(tuple(coverage.values())))
                    except Exception:
                        logger.exception("Unable to publish search progress.")

        tasks: dict[str, asyncio.Task] = {}
        try:
            tasks = {
                engine_name: asyncio.create_task(run_engine(engine_name, engine))
                for engine_name, engine in engines
            }

            # T-010: global wall-clock budget over the whole run (queueing
            # under the semaphore included). Pending engine tasks are
            # cancelled at the deadline; recorded variants keep their results.
            budget = max(0.0, self.settings.search_total_budget)
            _, pending = await asyncio.wait(
                tasks.values(),
                timeout=budget if budget > 0 else None,
            )
            if pending:
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                interrupted_names = sorted(
                    engine_name
                    for engine_name, task in tasks.items()
                    if task in pending
                )
                for engine_name in interrupted_names:
                    for query_index, query in enumerate(queries):
                        if engine_name in coverage[query]["engines"]:
                            continue
                        task_key = task_key_for(engine_name, query_index)
                        engine_errors[task_key] = TimeoutError("search budget exceeded")
                        engine_results[task_key] = []
                        coverage[query]["engines"][engine_name] = {
                            "status": "timeout",
                            "count": 0,
                        }
                logger.warning(
                    "Search budget of %.1fs exceeded; interrupted engines: %s",
                    budget,
                    ", ".join(interrupted_names),
                )
        finally:
            for task in tasks.values():
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks.values(), return_exceptions=True)
            await pool.close_all()

        attempted_count = len(engines) * len(queries)
        return engine_results, engine_errors, attempted_count, tuple(coverage.values())

    @staticmethod
    def _coverage_error_status(error: Exception) -> str:
        if isinstance(error, RobotChallengeError):
            return "challenge"
        if isinstance(error, TimeoutError) or "timeout" in str(error).lower():
            return "timeout"
        return "error"

    async def _search_engine_limited(
        self,
        semaphore: asyncio.Semaphore,
        engine_name: str,
        engine,
        parsed_query: str,
        browser,
        num_results: int,
    ) -> list[dict]:
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
    ) -> list[dict]:
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
