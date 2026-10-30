"""Single entry point for Zendriver/CDP access (T-020)."""

from browser.service import (
    BrowserService,
    click_at,
    eval_js,
    get_browser_service,
    mhtml,
    outer_html,
    page_layout,
    screenshot,
    visual_viewport,
)

__all__ = [
    "BrowserService",
    "click_at",
    "eval_js",
    "get_browser_service",
    "mhtml",
    "outer_html",
    "page_layout",
    "screenshot",
    "visual_viewport",
]
