import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from app.storage import BrowserStore
from app.profiles import ProfileLauncher, validate_web_url
from app.search import SearchRequest
from search_orchestrator import SearchOrchestrator
from tests.fakes import FakeBrowser
from tests.test_search_orchestrator import FakeEngine


class BrowserStoreTestCase(unittest.TestCase):
    def test_profiles_are_persistent_and_separate_without_touching_old_data(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "synthesix.db"
            legacy.write_bytes(b"existing investigation data")
            store = BrowserStore(root / "browser.sqlite")
            first = store.create_profile("Persona A")
            second = store.create_profile("Persona B")
            reopened = BrowserStore(root / "browser.sqlite")
            self.assertEqual(reopened.profiles(), [first, second])
            self.assertNotEqual(store.profile_path(first["id"]), store.profile_path(second["id"]))
            self.assertEqual(legacy.read_bytes(), b"existing investigation data")
            store.rename_profile(first["id"], "Renamed")
            self.assertEqual(reopened.profiles()[0]["name"], "Renamed")
            with self.assertRaises(ValueError):
                store.create_profile("renamed")
            with self.assertRaises(ValueError):
                store.profile_path("../../outside")

    def test_profile_path_rejects_symlink_escape(self):
        with TemporaryDirectory() as directory, TemporaryDirectory() as outside:
            store = BrowserStore(Path(directory) / "browser.sqlite")
            profile = store.create_profile("Test")
            path = store.profile_path(profile["id"])
            try:
                path.symlink_to(outside, target_is_directory=True)
            except OSError:
                if sys.platform != "win32":
                    raise
                import _winapi
                _winapi.CreateJunction(outside, str(path))
            with self.assertRaises(ValueError):
                store.profile_path(profile["id"])

    def test_search_roundtrip_keeps_request_results_and_partial_errors(self):
        with TemporaryDirectory() as directory:
            store = BrowserStore(Path(directory) / "browser.sqlite")
            request = {"queries": ["one", "two"], "automaticDorks": False}
            rows = [{"title": "Test", "link": "https://example.com/", "source": "Bing"}]
            run_id = store.save_search(request, rows, [{"query": "one", "engines": {}}], {"google": "timeout"})
            restored = store.search(run_id)
            self.assertEqual(restored["request"], request)
            self.assertEqual(restored["results"], rows)
            self.assertEqual(restored["errors"], {"google": "timeout"})
            self.assertEqual(store.history()[0]["count"], 1)
            self.assertEqual(store.history()[0]["id"], run_id)


class ProfileLauncherTestCase(unittest.TestCase):
    def test_native_launch_uses_own_profile_and_never_a_shell_or_debugging(self):
        with TemporaryDirectory() as directory:
            store = BrowserStore(Path(directory) / "browser.sqlite")
            profile = store.create_profile("Persona")
            with patch("app.profiles.subprocess.Popen") as launch:
                ProfileLauncher(store, Path("C:/Browser/chrome.exe")).open(profile["id"], "https://example.com/")
            args, kwargs = launch.call_args
            self.assertIn(f"--user-data-dir={store.profile_path(profile['id'])}", args[0])
            self.assertEqual(args[0][-1], "https://example.com/")
            self.assertFalse(kwargs.get("shell", False))
            self.assertFalse(any("remote-debugging" in value for value in args[0]))

    def test_non_web_urls_credentials_and_controls_are_rejected(self):
        for url in ["javascript:alert(1)", "file:///secret", "--incognito", "https://a:b@example.com", "https://example.com/\n--flag", "https:///no-host"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_web_url(url)
        self.assertEqual(validate_web_url("https://example.com/path?q=test"), "https://example.com/path?q=test")


class SearchRequestTestCase(unittest.TestCase):
    def test_multiple_queries_keep_explicit_dorks_and_exact_mode(self):
        request = SearchRequest.from_payload({"queries": ["Ada Lovelace", 'site:example.com "Grace Hopper"'], "engines": {"google": True}, "automaticDorks": True})
        self.assertEqual(request.queries[0], '"Ada Lovelace"')
        self.assertEqual(request.queries[1], 'site:example.com "Grace Hopper"')
        natural = SearchRequest.from_payload({"queries": ["Ada Lovelace"], "engines": {"bing": True}, "automaticDorks": False})
        self.assertEqual(natural.queries, ("Ada Lovelace",))

    def test_invalid_or_unbounded_payloads_are_rejected(self):
        for payload in [{}, {"queries": "one"}, {"queries": ["a"], "engines": {}}, {"queries": ["x" * 501], "engines": {"google": True}}, {"queries": ["a"], "engines": {"google": "false"}}, {"queries": [str(n) for n in range(21)], "engines": {"google": True}}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                SearchRequest.from_payload(payload)


class ProgressiveSearchTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_first_engine_results_arrive_before_slow_engine_finishes(self):
        released = asyncio.Event()
        fast_seen = asyncio.Event()
        fast = FakeEngine([{"title": "Ada", "description": "Ada", "link": "https://example.com/", "source": "Fast"}])

        class Slow:
            async def search(self, *_args):
                await released.wait()
                return []

        async def progress(rows, coverage):
            if rows and not fast_seen.is_set():
                self.assertFalse(released.is_set())
                self.assertEqual(coverage[0]["engines"]["fast"]["status"], "ok")
                fast_seen.set()

        report = Mock()
        orchestrator = SearchOrchestrator(engine_factories={"fast": lambda: fast, "slow": Slow}, report_generator=report)
        task = asyncio.create_task(orchestrator.collect("Ada", '"Ada"', FakeBrowser(), {"fast": True, "slow": True}, 10, on_progress=progress))
        try:
            await asyncio.wait_for(fast_seen.wait(), 2)
            self.assertFalse(task.done())
        finally:
            released.set()
        result = await task
        self.assertEqual(result.nb_results, 1)
        report.assert_not_called()

    async def test_cancel_closes_inflight_engine_tasks(self):
        started = asyncio.Event()
        closed = asyncio.Event()

        class Hanging:
            async def search(self, *_args):
                started.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    closed.set()

        orchestrator = SearchOrchestrator(engine_factories={"test": Hanging})
        task = asyncio.create_task(orchestrator.collect("a", "a", FakeBrowser(), {"test": True}, 10))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(closed.is_set())
