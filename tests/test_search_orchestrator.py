import asyncio
import unittest
from unittest.mock import patch

import pandas as pd

from exceptions import BrowserSessionError, RobotChallengeError, SearchEngineError
from query_operators import SearchFilters
from search_orchestrator import SearchOrchestrator, aggregate_search_results
from settings import get_settings


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


class AggregateSearchResultsTestCase(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
