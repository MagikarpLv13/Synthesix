"""Single entry point for Zendriver/CDP access (T-020)."""

from browser.service import (
    BrowserService,
    eval_js,
    get_browser_service,
    mhtml,
    outer_html,
    screenshot,
)

__all__ = [
    "BrowserService",
    "eval_js",
    "get_browser_service",
    "mhtml",
    "outer_html",
    "screenshot",
]
