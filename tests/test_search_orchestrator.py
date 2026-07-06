import asyncio
import unittest
from unittest.mock import patch

import pandas as pd

from exceptions import BrowserSessionError, RobotChallengeError, SearchEngineError
from query_operators import SearchFilters
from search_engine import SearchEngine
from search_orchestrator import SearchOrchestrator, aggregate_search_results
from settings import get_settings
from tests.fakes import FakeBrowser


class FakeEngine:
    def __init__(self, frame=None, exc=None):
        self.frame = frame if frame is not None else pd.DataFrame()
        self.exc = exc
        self.calls = []

    async def search(self, query, browser, max_results):
        self.calls.append((query, browser, max_results))
        if self.exc:
            raise self.exc
        return self.frame.copy()


class ReportCapture:
    def __init__(self):
        self.calls = []

    def __call__(self, df, query, total_time, nb_results):
        self.calls.append(
            {
                "df": df.copy(),
                "query": query,
                "total_time": total_time,
                "nb_results": nb_results,
            }
        )
        return "/tmp/synthesix-report.html"


class SequenceEngine:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    async def search(self, query, browser, max_results):
        self.calls.append((query, browser, max_results))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome.copy()


class SlowEngine:
    def __init__(self, delay):
        self.delay = delay
        self.calls = []

    async def search(self, query, browser, max_results):
        self.calls.append((query, browser, max_results))
        await asyncio.sleep(self.delay)
        return pd.DataFrame()


class HangingTabEngine(SearchEngine):
    """Real SearchEngine subclass that opens a tab then hangs forever.

    Exercises the T-010 cancellation path end to end: the budget cancels the
    task and ``SearchEngine.search``'s ``finally`` must still close the tab.
    """

    def __init__(self):
        super().__init__("Hanging")

    def set_selector(self):
        self.selector = "#results"

    def construct_url(self):
        return "https://hanging.example/search"

    def parse_results(self, raw_results):
        return []

    async def execute_search(self):
        self.tab = await self.browser.get(self.construct_url(), new_tab=True)
        await asyncio.sleep(999)


class ConcurrencyTrackingEngine:
    def __init__(self, tracker):
        self.tracker = tracker

    async def search(self, query, browser, max_results):
        self.tracker["active"] += 1
        self.tracker["max_active"] = max(self.tracker["max_active"], self.tracker["active"])
        try:
            await asyncio.sleep(0.01)
            return pd.DataFrame(
                [
                    {
                        "title": "Python async guide",
                        "link": "https://example.com/python-async",
                        "description": "A guide about Python async.",
                        "source": "Test",
                    }
                ]
            )
        finally:
            self.tracker["active"] -= 1


class QueryAwareEngine:
    def __init__(self, source):
        self.source = source
        self.calls = []

    async def search(self, query, browser, max_results):
        self.calls.append((query, browser, max_results))
        title = query.replace('"', "").title()
        return pd.DataFrame(
            [
                {
                    "title": title,
                    "link": "https://example.com/person",
                    "description": f"Result for {title}.",
                    "source": self.source,
                }
            ]
        )


class SearchOrchestratorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_search_passes_exact_query_to_enabled_engines(self):
        frame = pd.DataFrame(
            [
                {
                    "title": "Python async guide",
                    "link": "https://example.com/python-async",
                    "description": "A guide about Python async.",
                    "source": "DuckDuckGo",
                }
            ]
        )
        engine = FakeEngine(frame=frame)
        report_capture = ReportCapture()
        history_calls = []
        history_report_calls = []
        orchestrator = SearchOrchestrator(
            engine_factories={"duckduckgo": lambda: engine},
            report_generator=report_capture,
            history_adder=lambda *args: history_calls.append(args),
            history_report_generator=lambda: history_report_calls.append(True),
        )
        browser = object()

        result = await orchestrator.search(
            "python async",
            '"python async"',
            browser,
            {"duckduckgo": True},
            7,
        )

        self.assertEqual(engine.calls, [('"python async"', browser, 7)])
        self.assertEqual(result.output_path, "/tmp/synthesix-report.html")
        self.assertEqual(result.nb_results, 1)
        self.assertEqual(report_capture.calls[0]["query"], '"python async"')
        self.assertEqual(history_calls, [("python async", '"python async"', 1, "/tmp/synthesix-report.html")])
        self.assertEqual(history_report_calls, [True])
        self.assertEqual(result.results[0]["link"], "https://example.com/python-async")

    async def test_search_links_history_entry_to_investigation(self):
        frame = pd.DataFrame(
            [
                {
                    "title": "Example company registry",
                    "link": "https://example.com/company",
                    "description": "Registry entry.",
                    "source": "Google",
                }
            ]
        )
        history_calls = []
        orchestrator = SearchOrchestrator(
            engine_factories={"google": lambda: FakeEngine(frame=frame)},
            report_generator=ReportCapture(),
            history_adder=lambda *args, **kwargs: history_calls.append((args, kwargs)),
            history_report_generator=lambda: None,
        )

        result = await orchestrator.search(
            "example company",
            '"example company"',
            object(),
            {"google": True},
            5,
            investigation_id="case-123",
        )

        self.assertEqual(result.nb_results, 1)
        self.assertEqual(
            history_calls,
            [
                (
                    (
                        "example company",
                        '"example company"',
                        1,
                        "/tmp/synthesix-report.html",
                    ),
                    {"investigation_id": "case-123"},
                )
            ],
        )

    async def test_engine_failure_does_not_drop_successful_results(self):
        failing_engine = FakeEngine(exc=RuntimeError("boom"))
        successful_engine = FakeEngine(
            frame=pd.DataFrame(
                [
                    {
                        "title": "Python async guide",
                        "link": "https://example.com/python-async",
                        "description": "A guide about Python async.",
                        "source": "Bing",
                    }
                ]
            )
        )
        report_capture = ReportCapture()
        orchestrator = SearchOrchestrator(
            engine_factories={
                "google": lambda: failing_engine,
                "bing": lambda: successful_engine,
            },
            report_generator=report_capture,
            history_adder=lambda *_args: None,
            history_report_generator=lambda: None,
        )

        with self.assertLogs("search_orchestrator", level="ERROR") as logs:
            result = await orchestrator.search(
                "python async",
                '"python async"',
                object(),
                {"google": True, "bing": True},
                5,
            )

        self.assertIn("google", result.engine_errors)
        self.assertIsInstance(result.engine_errors["google"], SearchEngineError)
        self.assertEqual(result.nb_results, 1)
        self.assertEqual(report_capture.calls[0]["df"].iloc[0]["source"], "Bing")
        self.assertTrue(any("google search failed" in entry for entry in logs.output))

    async def test_all_engine_failures_raise_search_engine_error(self):
        report_capture = ReportCapture()
        orchestrator = SearchOrchestrator(
            engine_factories={
                "google": lambda: FakeEngine(exc=RuntimeError("google down")),
                "bing": lambda: FakeEngine(exc=RuntimeError("bing down")),
            },
            report_generator=report_capture,
            history_adder=lambda *_args: None,
            history_report_generator=lambda: None,
        )

        with self.assertLogs("search_orchestrator", level="ERROR"):
            with self.assertRaises(SearchEngineError) as raised:
                await orchestrator.search(
                    "python async",
                    '"python async"',
                    object(),
                    {"google": True, "bing": True},
                    5,
                )

        self.assertEqual(raised.exception.engine_name, "all")
        self.assertEqual(set(raised.exception.engine_errors), {"google", "bing"})
        self.assertEqual(report_capture.calls, [])

    async def test_retryable_browser_session_error_is_retried(self):
        frame = pd.DataFrame(
            [
                {
                    "title": "Python async guide",
                    "link": "https://example.com/python-async",
                    "description": "A guide about Python async.",
                    "source": "Google",
                }
            ]
        )
        engine = SequenceEngine([
            BrowserSessionError("temporary browser disconnect"),
            frame,
        ])
        report_capture = ReportCapture()

        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "1",
                "SYNTHESIX_ENGINE_RETRY_DELAY": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={"google": lambda: engine},
                report_generator=report_capture,
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            with self.assertLogs("search_orchestrator", level="WARNING") as logs:
                result = await orchestrator.search(
                    "python async",
                    '"python async"',
                    object(),
                    {"google": True},
                    5,
                )

        self.assertEqual(len(engine.calls), 2)
        self.assertEqual(result.nb_results, 1)
        self.assertEqual(result.engine_errors, {})
        self.assertTrue(any("retrying" in entry for entry in logs.output))

    async def test_robot_challenge_error_is_not_retried(self):
        engine = SequenceEngine([
            RobotChallengeError("Brave", "robot challenge"),
        ])

        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "3",
                "SYNTHESIX_ENGINE_RETRY_DELAY": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={"brave": lambda: engine},
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            with self.assertLogs("search_orchestrator", level="ERROR"):
                with self.assertRaises(RobotChallengeError):
                    await orchestrator.search(
                        "python async",
                        '"python async"',
                        object(),
                        {"brave": True},
                        5,
                    )

        self.assertEqual(len(engine.calls), 1)

    async def test_engine_timeout_is_limited_and_retried(self):
        engine = SlowEngine(delay=0.05)

        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_ENGINE_SEARCH_TIMEOUT": "0.01",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "1",
                "SYNTHESIX_ENGINE_RETRY_DELAY": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={"google": lambda: engine},
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            with self.assertLogs("search_orchestrator", level="ERROR"):
                with self.assertRaises(SearchEngineError) as raised:
                    await orchestrator.search(
                        "python async",
                        '"python async"',
                        object(),
                        {"google": True},
                        5,
                    )

        self.assertEqual(len(engine.calls), 2)
        self.assertIsInstance(raised.exception.original_error, TimeoutError)

    async def test_engine_concurrency_limit_is_respected(self):
        tracker = {"active": 0, "max_active": 0}

        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_ENGINE_CONCURRENCY": "1",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={
                    "google": lambda: ConcurrencyTrackingEngine(tracker),
                    "bing": lambda: ConcurrencyTrackingEngine(tracker),
                },
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            result = await orchestrator.search(
                "python async",
                '"python async"',
                object(),
                {"google": True, "bing": True},
                5,
            )

        self.assertEqual(tracker["max_active"], 1)
        self.assertEqual(result.nb_results, 1)

    async def test_enabled_engines_run_concurrently_by_default(self):
        tracker = {"active": 0, "max_active": 0}

        with patch.dict(
            "os.environ",
            {"SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "0"},
            clear=True,
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={
                    "google": lambda: ConcurrencyTrackingEngine(tracker),
                    "bing": lambda: ConcurrencyTrackingEngine(tracker),
                },
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            await orchestrator.search(
                "python async",
                '"python async"',
                object(),
                {"google": True, "bing": True},
                5,
            )

        self.assertEqual(tracker["max_active"], 2)

    async def test_search_budget_returns_partial_results_and_marks_timeouts(self):
        frame = pd.DataFrame(
            [
                {
                    "title": "Python async guide",
                    "link": "https://example.com/python-async",
                    "description": "A guide about Python async.",
                    "source": "Bing",
                }
            ]
        )
        fast_engine = FakeEngine(frame=frame)
        slow_engine = SlowEngine(delay=999)

        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_SEARCH_TOTAL_BUDGET": "0.05",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={
                    "bing": lambda: fast_engine,
                    "google": lambda: slow_engine,
                },
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            started = asyncio.get_running_loop().time()
            with self.assertLogs("search_orchestrator", level="WARNING") as logs:
                result = await orchestrator.search(
                    "python async",
                    '"python async"',
                    object(),
                    {"bing": True, "google": True},
                    5,
                )
            elapsed = asyncio.get_running_loop().time() - started

        self.assertLess(elapsed, 5.0)
        self.assertEqual(result.nb_results, 1)
        self.assertIn("google", result.engine_errors)
        self.assertIsInstance(result.engine_errors["google"], TimeoutError)
        self.assertEqual(str(result.engine_errors["google"]), "search budget exceeded")
        engines_coverage = result.coverage[0]["engines"]
        self.assertEqual(engines_coverage["google"], {"status": "timeout", "count": 0})
        self.assertEqual(engines_coverage["bing"]["status"], "ok")
        self.assertTrue(any("Search budget" in entry for entry in logs.output))

    async def test_search_budget_with_no_successful_engine_raises(self):
        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_SEARCH_TOTAL_BUDGET": "0.05",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={"google": lambda: SlowEngine(delay=999)},
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            with self.assertLogs("search_orchestrator", level="WARNING"):
                with self.assertRaises(TimeoutError):
                    await orchestrator.search(
                        "python async",
                        '"python async"',
                        object(),
                        {"google": True},
                        5,
                    )

    async def test_search_budget_cancellation_closes_engine_tabs(self):
        frame = pd.DataFrame(
            [
                {
                    "title": "Python async guide",
                    "link": "https://example.com/python-async",
                    "description": "A guide about Python async.",
                    "source": "Bing",
                }
            ]
        )
        hanging_engine = HangingTabEngine()
        browser = FakeBrowser()

        with patch.dict(
            "os.environ",
            {
                "SYNTHESIX_SEARCH_TOTAL_BUDGET": "0.05",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "0",
            },
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={
                    "bing": lambda: FakeEngine(frame=frame),
                    "google": lambda: hanging_engine,
                },
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            with self.assertLogs("search_orchestrator", level="WARNING"):
                result = await orchestrator.search(
                    "python async",
                    '"python async"',
                    browser,
                    {"bing": True, "google": True},
                    5,
                )

        self.assertEqual(result.nb_results, 1)
        self.assertEqual(len(browser.tabs), 1)
        self.assertTrue(browser.tabs[0].closed)
        self.assertIsNone(hanging_engine.tab)

    async def test_search_budget_zero_disables_the_deadline(self):
        frame = pd.DataFrame(
            [
                {
                    "title": "Python async guide",
                    "link": "https://example.com/python-async",
                    "description": "A guide about Python async.",
                    "source": "Bing",
                }
            ]
        )

        with patch.dict(
            "os.environ",
            {"SYNTHESIX_SEARCH_TOTAL_BUDGET": "0"},
        ):
            orchestrator = SearchOrchestrator(
                engine_factories={"bing": lambda: FakeEngine(frame=frame)},
                report_generator=ReportCapture(),
                history_adder=lambda *_args: None,
                history_report_generator=lambda: None,
                settings=get_settings(),
            )
            result = await orchestrator.search(
                "python async",
                '"python async"',
                object(),
                {"bing": True},
                5,
            )

        self.assertEqual(result.nb_results, 1)
        self.assertEqual(result.engine_errors, {})

    async def test_engine_specific_queries_are_used_for_filters(self):
        google_engine = FakeEngine()
        bing_engine = FakeEngine()
        orchestrator = SearchOrchestrator(
            engine_factories={
                "google": lambda: google_engine,
                "bing": lambda: bing_engine,
            },
            report_generator=ReportCapture(),
            history_adder=lambda *_args: None,
            history_report_generator=lambda: None,
        )
        browser = object()

        await orchestrator.search(
            "john doe",
            '"john doe" site:example.com intitle:profile inurl:admin',
            browser,
            {"google": True, "bing": True},
            5,
            filters=SearchFilters(site="example.com", title="profile", url="admin"),
            base_query='"john doe"',
        )

        self.assertEqual(
            google_engine.calls,
            [('"john doe" site:example.com intitle:profile inurl:admin', browser, 5)],
        )
        self.assertEqual(
            bing_engine.calls,
            [('"john doe" site:example.com intitle:profile admin', browser, 5)],
        )

    async def test_selected_query_variants_run_across_engines_and_merge_urls(self):
        instances = []

        def factory(source):
            def create():
                engine = QueryAwareEngine(source)
                instances.append(engine)
                return engine

            return create

        report_capture = ReportCapture()
        orchestrator = SearchOrchestrator(
            engine_factories={
                "google": factory("Google"),
                "bing": factory("Bing"),
            },
            report_generator=report_capture,
            history_adder=lambda *_args: None,
            history_report_generator=lambda: None,
        )

        result = await orchestrator.search(
            "anna lindberg",
            '"anna lindberg"',
            object(),
            {"google": True, "bing": True},
            5,
            base_query='"anna lindberg"',
            query_variants=('"anna lindberg"', '"lindberg anna"'),
        )

        self.assertEqual(len(instances), 4)
        self.assertEqual(result.nb_results, 1)
        self.assertEqual(len(result.coverage), 2)
        self.assertEqual(
            set(result.coverage[0]["engines"]),
            {"google", "bing"},
        )
        self.assertEqual(
            result.results[0]["query_variants"],
            ['"anna lindberg"', '"lindberg anna"'],
        )
        self.assertEqual(result.results[0]["source"], "Bing, Google")
        self.assertEqual(
            report_capture.calls[0]["df"].attrs["query_coverage"],
            result.coverage,
        )
        self.assertEqual(
            report_capture.calls[0]["df"].attrs["search_context"],
            {
                "original_query": "anna lindberg",
                "filters": {},
                "num_results": 5,
                "investigation_id": "",
            },
        )


class AggregateSearchResultsTestCase(unittest.TestCase):
    def test_results_are_sorted_by_descending_relevance(self):
        engine_results = {
            "google": pd.DataFrame(
                [
                    {
                        "title": "Low",
                        "link": "https://example.com/low",
                        "description": "Low result.",
                        "source": "Google",
                    },
                    {
                        "title": "High",
                        "link": "https://example.com/high",
                        "description": "High result.",
                        "source": "Google",
                    },
                ]
            )
        }

        combined = aggregate_search_results(
            engine_results,
            "query",
            scorer=lambda row, _query: 10 if row["title"] == "High" else 1,
        )

        self.assertEqual(combined["title"].tolist(), ["High", "Low"])
        self.assertEqual(combined.index.tolist(), [0, 1])

    def test_deduplicates_links_and_merges_sources(self):
        engine_results = {
            "google": pd.DataFrame(
                [
                    {
                        "title": "Python async guide",
                        "link": "https://example.com/python-async",
                        "description": "A guide.",
                        "source": "Google",
                    },
                    {
                        "title": "Other result",
                        "link": "https://example.com/other",
                        "description": "No match.",
                        "source": "Google",
                    },
                ]
            ),
            "bing": pd.DataFrame(
                [
                    {
                        "title": "Async Python reference",
                        "link": "https://example.com/python-async",
                        "description": "Python async reference.",
                        "source": "Bing",
                    }
                ]
            ),
        }

        combined = aggregate_search_results(engine_results, '"python async"')

        duplicate_row = combined[combined["link"] == "https://example.com/python-async"].iloc[0]
        self.assertEqual(duplicate_row["source"], "Bing, Google")
        self.assertEqual(duplicate_row["engine_count"], 2)
        self.assertIn(
            "engine_consensus",
            [component["key"] for component in duplicate_row["score_breakdown"]],
        )
        self.assertEqual(len(combined), 2)
        self.assertIn("relevance_score", combined.columns)

    def test_filters_results_after_engine_search(self):
        engine_results = {
            "bing": pd.DataFrame(
                [
                    {
                        "title": "John Doe profile",
                        "link": "https://example.com/admin/profile.pdf",
                        "description": "John Doe reference.",
                        "source": "Bing",
                    },
                    {
                        "title": "John Doe profile",
                        "link": "https://example.com/public/profile.html",
                        "description": "John Doe reference.",
                        "source": "Bing",
                    },
                ]
            )
        }

        combined = aggregate_search_results(
            engine_results,
            '"john doe" site:example.com inurl:admin filetype:pdf',
            filters=SearchFilters(site="example.com", url="admin", filetype="pdf"),
            base_query='"john doe"',
        )

        self.assertEqual(len(combined), 1)
        self.assertEqual(combined.iloc[0]["link"], "https://example.com/admin/profile.pdf")

    def test_filter_only_search_keeps_matching_results_with_minimum_score(self):
        engine_results = {
            "google": pd.DataFrame(
                [
                    {
                        "title": "Document",
                        "link": "https://example.com/report.pdf",
                        "description": "Reference.",
                        "source": "Google",
                    }
                ]
            )
        }

        combined = aggregate_search_results(
            engine_results,
            "site:example.com filetype:pdf",
            filters=SearchFilters(site="example.com", filetype="pdf"),
            base_query="",
        )

        self.assertEqual(len(combined), 1)
        self.assertEqual(combined.iloc[0]["relevance_score"], 1.0)
        self.assertEqual(
            combined.iloc[0]["score_breakdown"][0]["key"],
            "filter_match",
        )


if __name__ == "__main__":
    unittest.main()
