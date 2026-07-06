"""Fake Zendriver browser/tab harness shared by Synthesix tests (T-050).

Reference: zendriver 0.15.3. The fakes only cover the methods the code base
actually calls; grep real usages before extending them, and keep signatures
aligned with zendriver.

Every fake method resolves its return value in this order:
1. a programmed side effect queued with ``tab.program("evaluate", ...)``
   (an Exception instance is raised, a callable is invoked with the call
   arguments, anything else is returned as-is);
2. a handler registered with ``tab.on("evaluate", func)`` (called with the
   positional arguments — useful when responses depend on the script);
3. the per-method default (None / [] / "" / self).

All calls are recorded in a :class:`CallJournal` shared between a browser and
the tabs it creates, so tests can assert CDP budgets:
``journal.count("evaluate")``, ``journal.scripts_evaluated_bytes()``.

Example 1 — engine wait (timeout without real time)::

    import search_engine as search_engine_module
    from tests.fakes import FakeTab, fake_clock

    tab = FakeTab(url="https://engine.example/search")
    engine.tab = tab                      # concrete SearchEngine subclass
    with fake_clock(search_engine_module) as clock:
        loaded = await engine.wait_for_page_load(timeout=30, interval=0.5)
    # clock.now advanced past 30s, but no real time was spent sleeping.

Example 2 — home action loop::

    from tests.fakes import FakeBrowser, FakeTab

    home = FakeTab(url=INDEX_URL, target_id="home")
    home.on("evaluate", my_home_script_handler)   # answers consumeAction etc.
    browser = FakeBrowser([home])
    action = await wait_for_home_action(browser, INDEX_URL, settings=settings)

Example 3 — capture::

    tab = FakeTab()
    tab.program("send", base64.b64encode(b"png-bytes").decode("ascii"))
    captured = await capture_png(tab, path, {"x": 0, "y": 0, "width": 4, "height": 4})
    assert tab.journal.count("send") == 1
"""

from __future__ import annotations

import asyncio
import time
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Iterator
from unittest.mock import patch

_REAL_ASYNCIO_SLEEP = asyncio.sleep
_REAL_MONOTONIC = time.monotonic


@dataclass
class CallRecord:
    method: str
    args: tuple
    kwargs: dict
    at: float


class CallJournal:
    """Timestamped log of every fake call, shared browser <-> tabs."""

    def __init__(self) -> None:
        self.records: list[CallRecord] = []

    def record(self, method: str, args: tuple, kwargs: dict) -> None:
        self.records.append(CallRecord(method, args, kwargs, _REAL_MONOTONIC()))

    def calls(self, method: str) -> list[CallRecord]:
        return [record for record in self.records if record.method == method]

    def count(self, method: str) -> int:
        return len(self.calls(method))

    def scripts_evaluated_bytes(self) -> int:
        return sum(
            len(str(record.args[0]).encode("utf-8"))
            for record in self.calls("evaluate")
            if record.args
        )


class FakeElement:
    """Minimal DOM node double (truthy, clickable)."""

    def __init__(self, text: str = "", attrs: dict | None = None) -> None:
        self.text = text
        self.attrs = dict(attrs or {})
        self.clicks = 0

    async def click(self) -> None:
        self.clicks += 1

    def __getitem__(self, key: str) -> Any:
        return self.attrs[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.attrs.get(key, default)


class FakeTab:
    """Scriptable stand-in for ``zendriver.Tab`` (see module docstring)."""

    _DEFAULTS: dict[str, Any] = {
        "evaluate": None,
        "query_selector": None,
        "xpath": [],
        "find": None,
        "get_content": "",
        "send": None,
        "save_screenshot": None,
        "bring_to_front": None,
        "reload": None,
    }

    def __init__(
        self,
        url: str = "about:blank",
        target_id: str = "fake-tab",
        journal: CallJournal | None = None,
    ) -> None:
        self.url = url
        self.target_id = target_id
        self.closed = False
        self.journal = journal if journal is not None else CallJournal()
        self._side_effects: dict[str, list[Any]] = {}
        self._handlers: dict[str, Callable] = {}

    # -- programming -----------------------------------------------------

    def program(self, method: str, *responses: Any) -> "FakeTab":
        """Queue successive responses for ``method`` (FIFO)."""
        self._side_effects.setdefault(method, []).extend(responses)
        return self

    def on(self, method: str, handler: Callable) -> "FakeTab":
        """Fallback handler called with the call's positional arguments."""
        self._handlers[method] = handler
        return self

    def _resolve(self, method: str, args: tuple, kwargs: dict) -> Any:
        self.journal.record(method, args, kwargs)
        queue = self._side_effects.get(method)
        if queue:
            response = queue.pop(0)
            if isinstance(response, BaseException):
                raise response
            if callable(response):
                return response(*args, **kwargs)
            return response
        handler = self._handlers.get(method)
        if handler is not None:
            return handler(*args)
        return self._DEFAULTS.get(method)

    # -- zendriver.Tab surface -------------------------------------------

    async def evaluate(self, script: str, *args: Any, **kwargs: Any) -> Any:
        return self._resolve("evaluate", (script, *args), kwargs)

    async def query_selector(self, selector: str, *args: Any, **kwargs: Any) -> Any:
        return self._resolve("query_selector", (selector, *args), kwargs)

    async def xpath(self, expression: str, *args: Any, **kwargs: Any) -> Any:
        return self._resolve("xpath", (expression, *args), kwargs)

    async def find(self, text: str, *args: Any, **kwargs: Any) -> Any:
        return self._resolve("find", (text, *args), kwargs)

    async def get_content(self) -> str:
        return self._resolve("get_content", (), {})

    async def get(self, url: str, *args: Any, **kwargs: Any) -> "FakeTab":
        result = self._resolve("get", (url, *args), kwargs)
        if result is not None:
            return result
        self.url = url
        return self

    async def send(self, command: Any, *args: Any, **kwargs: Any) -> Any:
        return self._resolve("send", (command, *args), kwargs)

    async def save_screenshot(self, *args: Any, **kwargs: Any) -> Any:
        return self._resolve("save_screenshot", args, kwargs)

    async def bring_to_front(self) -> None:
        return self._resolve("bring_to_front", (), {})

    async def reload(self, *args: Any, **kwargs: Any) -> None:
        return self._resolve("reload", args, kwargs)

    async def close(self) -> None:
        self._resolve("close", (), {})
        self.closed = True


class _FakeCookies:
    def __init__(self, journal: CallJournal) -> None:
        self._journal = journal

    async def clear(self) -> None:
        self._journal.record("cookies.clear", (), {})


class FakeBrowser:
    """Scriptable stand-in for ``zendriver.Browser`` (see module docstring)."""

    def __init__(
        self,
        tabs: list[FakeTab] | None = None,
        journal: CallJournal | None = None,
    ) -> None:
        self.journal = journal if journal is not None else CallJournal()
        self.tabs: list[FakeTab] = list(tabs or [])
        for tab in self.tabs:
            tab.journal = self.journal
        self.stopped = False
        self.cookies = _FakeCookies(self.journal)
        self._tab_counter = 0

    @property
    def main_tab(self) -> FakeTab | None:
        return self.tabs[0] if self.tabs else None

    def new_tab(self, url: str = "about:blank") -> FakeTab:
        self._tab_counter += 1
        tab = FakeTab(
            url=url,
            target_id=f"fake-tab-{self._tab_counter}",
            journal=self.journal,
        )
        self.tabs.append(tab)
        return tab

    async def get(self, url: str, new_tab: bool = False) -> FakeTab:
        self.journal.record("browser.get", (url,), {"new_tab": new_tab})
        if new_tab or self.main_tab is None:
            return self.new_tab(url)
        self.main_tab.url = url
        return self.main_tab

    async def update_targets(self) -> None:
        self.journal.record("update_targets", (), {})

    async def _get_targets(self) -> list:
        self.journal.record("_get_targets", (), {})
        return [
            type("Target", (), {"target_id": tab.target_id, "type_": "page"})()
            for tab in self.tabs
        ]

    async def stop(self) -> None:
        self.journal.record("stop", (), {})
        self.stopped = True


class FakeClock:
    """Injectable monotonic clock; ``sleep`` advances it without real time."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = float(start)
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += float(seconds)

    async def sleep(self, delay: float) -> None:
        self.sleeps.append(delay)
        self.now += max(0.0, float(delay))
        # Yield to the event loop so concurrent tasks still interleave.
        await _REAL_ASYNCIO_SLEEP(0)


class _ModuleProxy:
    """Pass-through module wrapper overriding a handful of attributes."""

    def __init__(self, real: Any, **overrides: Any) -> None:
        self._real = real
        self._overrides = overrides

    def __getattr__(self, name: str) -> Any:
        if name in self._overrides:
            return self._overrides[name]
        return getattr(self._real, name)


@contextmanager
def fake_clock(*modules: Any, start: float = 0.0) -> Iterator[FakeClock]:
    """Patch ``time.monotonic`` and ``asyncio.sleep`` inside ``modules``.

    Only the named modules see the fake clock (their module-level ``time`` /
    ``asyncio`` references are wrapped); the rest of the process keeps the
    real ones, so the event loop itself is unaffected.
    """
    clock = FakeClock(start)
    with ExitStack() as stack:
        for module in modules:
            if hasattr(module, "time"):
                stack.enter_context(
                    patch.object(
                        module, "time", _ModuleProxy(time, monotonic=clock.monotonic)
                    )
                )
            if hasattr(module, "asyncio"):
                stack.enter_context(
                    patch.object(
                        module, "asyncio", _ModuleProxy(asyncio, sleep=clock.sleep)
                    )
                )
        yield clock
