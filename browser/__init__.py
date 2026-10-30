"""Single entry point for Zendriver/CDP access (T-020)."""

from browser.service import (
    BrowserService,
    click_at,
    eval_js,
    get_browser_service,
    mhtml,
    monitor_probe_page_state,
    monitor_probe_snapshot,
    outer_html,
    page_layout,
    screenshot,
    visual_viewport,
)
from browser.social import social_profile_snapshot

__all__ = [
    "BrowserService",
    "click_at",
    "eval_js",
    "get_browser_service",
    "mhtml",
    "monitor_probe_page_state",
    "monitor_probe_snapshot",
    "outer_html",
    "page_layout",
    "screenshot",
    "social_profile_snapshot",
    "visual_viewport",
]
