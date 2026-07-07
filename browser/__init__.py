"""Single entry point for Zendriver/CDP access (T-020)."""

from browser.service import (
    BrowserService,
    click_at,
    eval_js,
    get_browser_service,
    mhtml,
    outer_html,
    screenshot,
)

__all__ = [
    "BrowserService",
    "click_at",
    "eval_js",
    "get_browser_service",
    "mhtml",
    "outer_html",
    "screenshot",
]
