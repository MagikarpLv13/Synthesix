import unittest

import pandas as pd

from exceptions import SearchEngineError
from search_orchestrator import SearchOrchestrator, aggregate_search_results


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


if __name__ == "__main__":
    unittest.main()
