import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from types import SimpleNamespace
from unittest.mock import AsyncMock

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


class BrowserRuntimeTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_repeated_cancel_does_not_interrupt_search_cleanup(self):
        from app.runtime import BrowserApplication
        with TemporaryDirectory() as directory:
            app = BrowserApplication(SimpleNamespace(base_dir=Path(directory)))
            cleaning = asyncio.Event()
            finish = asyncio.Event()
            completed = asyncio.Event()
            async def work():
                try:
                    await asyncio.Event().wait()
                finally:
                    cleaning.set()
                    await finish.wait()
                    completed.set()
            app.search_task = asyncio.create_task(work())
            await asyncio.sleep(0)
            with patch.object(app, "trusted_source", new=AsyncMock(return_value=True)):
                await app.dispatch({"action": "cancel_search"}, object())
                await cleaning.wait()
                await app.dispatch({"action": "cancel_search"}, object())
                finish.set()
                await asyncio.gather(app.search_task, return_exceptions=True)
            self.assertTrue(completed.is_set())

    async def test_unresponsive_ui_evaluation_is_bounded(self):
        from browser import eval_js
        stopped = asyncio.Event()
        async def hanging(_script):
            try:
                await asyncio.Event().wait()
            finally:
                stopped.set()
        with patch("browser.service.EVALUATE_TIMEOUT_SECONDS", .01):
            self.assertIsNone(await eval_js(SimpleNamespace(evaluate=hanging), "true", category="test"))
        self.assertTrue(stopped.is_set())

    async def test_target_registry_refresh_keeps_the_initialized_home_connection(self):
        from app.runtime import BrowserApplication
        with TemporaryDirectory() as directory:
            app = BrowserApplication(SimpleNamespace(base_dir=Path(directory)))
            initialized = SimpleNamespace(target_id="home", url=app.home_url)
            app.service = SimpleNamespace(arm_dispatch_binding=AsyncMock())
            await app.select_home([initialized])
            refreshed = SimpleNamespace(target_id="home", url=app.home_url)
            await app.select_home([refreshed])
            self.assertIs(app.home_tab, initialized)
            app.service.arm_dispatch_binding.assert_awaited_once_with(initialized)
            await app.select_home([SimpleNamespace(target_id="home", url="https://example.com/")])
            self.assertIsNone(app.home_tab)
            await app.select_home([refreshed])
            self.assertIs(app.home_tab, initialized)

    async def test_foreign_tabs_and_navigated_home_cannot_issue_privileged_actions(self):
        from app.runtime import BrowserApplication
        with TemporaryDirectory() as directory:
            app = BrowserApplication(SimpleNamespace(base_dir=Path(directory)))
            app.home_tab = SimpleNamespace(target_id="home")
            with patch("app.runtime.eval_js", new_callable=AsyncMock, return_value="https://example.com/"):
                await app.dispatch({"action": "create_profile", "name": "Forbidden"}, app.home_tab)
                await app.dispatch({"action": "create_profile", "name": "Forbidden"}, SimpleNamespace(target_id="external"))
            self.assertEqual(app.store.profiles(), [])

    async def test_home_commands_create_profile_but_cannot_open_non_web_url(self):
        from app.runtime import BrowserApplication
        with TemporaryDirectory() as directory:
            app = BrowserApplication(SimpleNamespace(base_dir=Path(directory)))
            app.home_tab = SimpleNamespace(target_id="home")
            app.service = SimpleNamespace(open_tab=AsyncMock())
            with patch("app.runtime.eval_js", new_callable=AsyncMock, return_value=app.home_url):
                await app.dispatch({"action": "create_profile", "name": "Persona"}, app.home_tab)
                await app.dispatch({"action": "open_result", "url": "file:///private", "profileId": ""}, app.home_tab)
            self.assertEqual(app.store.profiles()[0]["name"], "Persona")
            app.service.open_tab.assert_not_called()
            self.assertTrue(app.model["isError"])

    async def test_idle_heartbeat_does_not_transfer_results_again(self):
        from app.runtime import BrowserApplication
        with TemporaryDirectory() as directory:
            app = BrowserApplication(SimpleNamespace(base_dir=Path(directory)))
            app.home_tab = SimpleNamespace(target_id="home")
            app.model["results"] = [{"title": "SYNTHETIC_LARGE_PAYLOAD"}]
            with patch("app.runtime.eval_js", new_callable=AsyncMock, return_value=True) as evaluate:
                await app.publish()
            self.assertNotIn("SYNTHETIC_LARGE_PAYLOAD", evaluate.call_args.args[1])

    def test_entrypoint_imports_no_investigation_modules(self):
        script = "import main,sys,json; print(json.dumps([m for m in sys.modules if m.split('.')[0] in {'investigations','evidence','exports','analysis'}]))"
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), [])

    def test_search_runtime_imports_no_report_renderer(self):
        script = "import app.runtime,sys,json; print(json.dumps([m for m in ('ui','utils','investigations','evidence','exports','analysis') if m in sys.modules]))"
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), [])
