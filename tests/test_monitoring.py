import unittest
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from browser import BrowserService, social_profile_snapshot
from exceptions import InvestigationValidationError
from investigations.monitoring import (
    DEFAULT_MONITOR_ARCHIVE_POLICY,
    DEFAULT_CHECK_INTERVAL_MINUTES,
    infer_monitor_profile,
    resolve_monitor_configuration,
)
from investigations.probe import (
    PageMonitorProbe,
    ProbeResult,
    _normalize_metric,
    compare_metric_values,
    observation_content_sha256,
)
from investigations.repository import InvestigationRepository
from investigations.scheduler import (
    MonitorSchedulerOptions,
    PageMonitorScheduler,
)
from investigations.service import InvestigationService
from investigations.social_adapters import (
    SocialAdapterRegistry,
    SocialApiCredentials,
    SocialApiRequestError,
)
from tests.fakes import FakeBrowser


class MonitorConfigurationTestCase(unittest.TestCase):
    def test_infers_supported_social_profiles_from_url(self):
        cases = {
            "https://www.facebook.com/example": "facebook_page",
            "https://instagram.com/example/": "instagram_profile",
            "https://www.tiktok.com/@example": "tiktok_profile",
            "https://x.com/example": "x_profile",
            "https://mobile.twitter.com/example": "x_profile",
            "https://youtube.com/@example": "youtube_channel",
            "https://instagram.com/p/post-id/": "generic_page",
            "https://tiktok.com/video-id": "generic_page",
            "https://x.com/example/status/123": "generic_page",
            "https://youtube.com/watch?v=123": "generic_page",
            "https://youtu.be/123": "generic_page",
            "https://facebook.com/watch/123": "generic_page",
            "https://example.org/about": "generic_page",
        }

        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(infer_monitor_profile(url), expected)

    def test_automatic_mode_selects_profile_but_accepts_metric_choice(self):
        configuration = resolve_monitor_configuration(
            "https://instagram.com/example/",
            {
                "mode": "automatic",
                "metrics": ["followers", "posts"],
            },
        )

        self.assertEqual(configuration.mode, "automatic")
        self.assertEqual(configuration.profile, "instagram_profile")
        self.assertEqual(configuration.metrics, ("followers", "posts"))
        self.assertEqual(
            configuration.check_interval_minutes,
            DEFAULT_CHECK_INTERVAL_MINUTES,
        )
        self.assertTrue(configuration.is_enabled)
        self.assertEqual(
            configuration.archive_policy,
            DEFAULT_MONITOR_ARCHIVE_POLICY,
        )

    def test_custom_mode_preserves_selectors_and_interval(self):
        configuration = resolve_monitor_configuration(
            "https://shop.example/product",
            {
                "mode": "custom",
                "profile": "generic_page",
                "metrics": ["price", "availability"],
                "selectors": {
                    "price": "[data-price]",
                    "availability": ".stock-status",
                },
                "check_interval_minutes": 60,
                "is_enabled": False,
                "archive_policy": "never",
            },
        )

        self.assertEqual(configuration.mode, "custom")
        self.assertEqual(configuration.profile, "generic_page")
        self.assertEqual(configuration.metrics, ("price", "availability"))
        self.assertEqual(
            configuration.selectors,
            {
                "price": "[data-price]",
                "availability": ".stock-status",
            },
        )
        self.assertEqual(configuration.check_interval_minutes, 60)
        self.assertFalse(configuration.is_enabled)
        self.assertEqual(configuration.archive_policy, "never")

    def test_facebook_defaults_include_stable_profile_and_post_metrics(self):
        configuration = resolve_monitor_configuration(
            "https://facebook.com/profile.php?id=123",
            {"mode": "automatic"},
        )

        self.assertEqual(configuration.profile, "facebook_page")
        self.assertTrue(
            {
                "display_name",
                "friends_count",
                "profile_photo",
                "cover_photo",
                "bio",
                "profile_details",
                "latest_post_id",
                "latest_post_date",
                "latest_post_content",
                "latest_post_permalink",
            }.issubset(configuration.metrics)
        )
        self.assertEqual(
            configuration.storage_payload()["schema_version"],
            2,
        )

    def test_rejects_selector_for_unselected_metric(self):
        with self.assertRaisesRegex(
            InvestigationValidationError,
            "unselected metric",
        ):
            resolve_monitor_configuration(
                "https://example.org",
                {
                    "mode": "custom",
                    "metrics": ["price"],
                    "selectors": {"availability": ".stock"},
                },
            )

    def test_rejects_unsafe_metric_identifier_and_interval(self):
        with self.assertRaisesRegex(
            InvestigationValidationError,
            "metric identifier",
        ):
            resolve_monitor_configuration(
                "https://example.org",
                {
                    "mode": "custom",
                    "metrics": ["document.querySelector('body')"],
                },
            )

        with self.assertRaisesRegex(
            InvestigationValidationError,
            "between 15 and 43200",
        ):
            resolve_monitor_configuration(
                "https://example.org",
                {"check_interval_minutes": 5},
            )

        with self.assertRaisesRegex(
            InvestigationValidationError,
            "archive policy",
        ):
            resolve_monitor_configuration(
                "https://example.org",
                {"archive_policy": "always"},
            )


class MonitorComparisonTestCase(unittest.TestCase):
    def test_compares_numbers_text_lists_and_states(self):
        minor_number = compare_metric_values(
            {"status": "ok", "kind": "number", "value": 100},
            {"status": "ok", "kind": "number", "value": 101},
        )
        changed_number = compare_metric_values(
            {"status": "ok", "kind": "number", "value": 100},
            {"status": "ok", "kind": "number", "value": 150},
        )
        unchanged_list = compare_metric_values(
            {"status": "ok", "kind": "list", "value": ["a", "b"]},
            {"status": "ok", "kind": "list", "value": ["b", "a"]},
        )
        changed_state = compare_metric_values(
            {"status": "ok", "kind": "state", "value": True},
            {"status": "ok", "kind": "state", "value": False},
        )
        changed_text = compare_metric_values(
            {"status": "ok", "kind": "text", "value": "Original page"},
            {
                "status": "ok",
                "kind": "text",
                "value": "Completely different content",
            },
        )

        self.assertEqual(minor_number["status"], "minor_change")
        self.assertEqual(changed_number["status"], "changed")
        self.assertEqual(unchanged_list["status"], "unchanged")
        self.assertEqual(changed_state["status"], "changed")
        self.assertEqual(changed_text["status"], "changed")

    def test_missing_unavailable_and_error_never_become_zero(self):
        for status in ("missing", "unavailable", "error"):
            with self.subTest(status=status):
                change = compare_metric_values(
                    {"status": "ok", "kind": "number", "value": 0},
                    {"status": status, "kind": "number", "value": None},
                )
                self.assertNotEqual(change.get("current_status"), "ok")

    def test_observation_hash_ignores_list_order_but_keeps_status(self):
        first = observation_content_sha256(
            {
                "links": {
                    "status": "ok",
                    "kind": "list",
                    "value": ["https://b.example", "https://a.example"],
                }
            }
        )
        reordered = observation_content_sha256(
            {
                "links": {
                    "status": "ok",
                    "kind": "list",
                    "value": ["https://a.example", "https://b.example"],
                }
            }
        )
        missing = observation_content_sha256(
            {
                "links": {
                    "status": "missing",
                    "kind": "list",
                    "value": None,
                }
            }
        )

        self.assertEqual(first, reordered)
        self.assertNotEqual(first, missing)

    def test_comparison_key_ignores_volatile_display_value(self):
        previous = {
            "status": "ok",
            "kind": "text",
            "value": "https://cdn.example/photo.jpg?token=old",
            "comparison_key": "photo.jpg",
        }
        current = {
            "status": "ok",
            "kind": "text",
            "value": "https://cdn.example/photo.jpg?token=new",
            "comparison_key": "photo.jpg",
        }
        normalized = _normalize_metric(current)

        self.assertEqual(normalized["comparison_key"], "photo.jpg")
        self.assertEqual(
            compare_metric_values(previous, current)["status"],
            "unchanged",
        )
        self.assertEqual(
            observation_content_sha256({"photo": previous}),
            observation_content_sha256({"photo": current}),
        )


class _SocialHttpClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    async def request_json(
        self,
        method,
        url,
        *,
        headers=None,
        body=None,
        timeout=10.0,
    ):
        self.requests.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers or {}),
                "body": dict(body or {}),
                "timeout": timeout,
            }
        )
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class SocialAdapterTestCase(unittest.IsolatedAsyncioTestCase):
    def test_registry_maps_supported_profile_urls(self):
        registry = SocialAdapterRegistry()

        self.assertEqual(
            registry.for_url("https://instagram.com/example").name,
            "instagram",
        )
        self.assertEqual(
            registry.for_url("https://x.com/example").name,
            "x",
        )
        self.assertIsNone(registry.for_url("https://example.org/page"))

    async def test_youtube_api_marks_subscribers_as_rounded(self):
        http = _SocialHttpClient(
            [
                {
                    "items": [
                        {
                            "snippet": {
                                "title": "Example channel",
                                "description": "Official description",
                            },
                            "statistics": {
                                "subscriberCount": "123000",
                                "hiddenSubscriberCount": False,
                                "videoCount": "42",
                                "viewCount": "987654",
                            },
                        }
                    ]
                }
            ]
        )
        registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(
                youtube_api_key="youtube-secret",
            ),
            http_client=http,
        )

        result = await registry.get("youtube_channel").extract_api(
            "https://youtube.com/@example",
            (
                "channel_name",
                "description",
                "subscribers",
                "videos",
                "views",
            ),
        )

        self.assertEqual(result.metrics["subscribers"]["value"], 123000)
        self.assertEqual(
            result.metrics["subscribers"]["precision"],
            "rounded",
        )
        self.assertEqual(
            result.metrics["subscribers"]["provenance"]["source"],
            "api",
        )
        self.assertEqual(result.metrics["videos"]["precision"], "exact")
        self.assertIn("forHandle=%40example", http.requests[0]["url"])
        self.assertNotIn(
            "youtube-secret",
            repr(result),
        )

    async def test_x_api_and_tiktok_research_api_parse_public_metrics(self):
        x_http = _SocialHttpClient(
            [
                {
                    "data": {
                        "name": "Example",
                        "description": "Bio",
                        "url": "https://example.org",
                        "entities": {},
                        "public_metrics": {
                            "followers_count": 1200,
                            "following_count": 42,
                            "tweet_count": 900,
                            "listed_count": 15,
                        },
                    }
                }
            ]
        )
        x_registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(
                x_bearer_token="x-secret",
            ),
            http_client=x_http,
        )
        x_result = await x_registry.get("x_profile").extract_api(
            "https://x.com/example",
            (
                "profile_name",
                "bio",
                "followers",
                "following",
                "posts",
                "listed",
                "external_links",
            ),
        )

        self.assertEqual(x_result.metrics["followers"]["value"], 1200)
        self.assertEqual(x_result.metrics["posts"]["value"], 900)
        self.assertEqual(
            x_result.metrics["external_links"]["value"],
            ["https://example.org"],
        )
        self.assertEqual(
            x_http.requests[0]["headers"]["Authorization"],
            "Bearer x-secret",
        )

        tiktok_http = _SocialHttpClient(
            [
                {
                    "data": {
                        "display_name": "TikTok example",
                        "bio_description": "Research profile",
                        "follower_count": 50,
                        "following_count": 5,
                        "likes_count": 700,
                        "video_count": 12,
                        "bio_url": "https://example.net",
                    },
                    "error": {"code": "ok"},
                }
            ]
        )
        tiktok_registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(
                tiktok_research_access_token="tiktok-secret",
            ),
            http_client=tiktok_http,
        )
        tiktok_result = await tiktok_registry.get(
            "tiktok_profile"
        ).extract_api(
            "https://tiktok.com/@example",
            ("profile_name", "followers", "posts", "likes"),
        )

        self.assertEqual(tiktok_result.metrics["followers"]["value"], 50)
        self.assertEqual(tiktok_result.metrics["posts"]["value"], 12)
        self.assertEqual(
            tiktok_http.requests[0]["body"],
            {"username": "example"},
        )

    def test_instagram_dom_parser_handles_rounded_counts_and_links(self):
        adapter = SocialAdapterRegistry().get("instagram_profile")
        result = adapter.extract_dom(
            {
                "metadata": {},
                "signals": {
                    "og_title": (
                        "Example (@example) • Instagram photos and videos"
                    ),
                    "og_description": (
                        "1.2M Followers, 34 Following, 56 Posts - "
                        "Open source investigator"
                    ),
                    "links": [
                        {"href": "https://instagram.com/example"},
                        {"href": "https://example.org/profile"},
                    ],
                    "labeled_texts": [],
                    "body_text": "",
                    "json_ld": [],
                },
                "custom_metrics": {},
            },
            (
                "profile_name",
                "bio",
                "followers",
                "following",
                "posts",
                "external_links",
            ),
        )

        self.assertEqual(
            result.metrics["profile_name"]["value"],
            "Example (@example)",
        )
        self.assertEqual(
            result.metrics["bio"]["value"],
            "Open source investigator",
        )
        self.assertEqual(result.metrics["followers"]["value"], 1_200_000)
        self.assertEqual(
            result.metrics["followers"]["precision"],
            "rounded",
        )
        self.assertEqual(result.metrics["following"]["value"], 34)
        self.assertEqual(result.metrics["posts"]["value"], 56)
        self.assertEqual(
            result.metrics["external_links"]["value"],
            ["https://example.org/profile"],
        )

    def test_facebook_dom_parser_extracts_profile_and_latest_post(self):
        adapter = SocialAdapterRegistry().get("facebook_page")
        result = adapter.extract_dom(
            {
                "metadata": {},
                "signals": {
                    "og_title": "Facebook",
                    "og_description": "",
                    "links": [],
                    "labeled_texts": [],
                    "body_text": "",
                    "json_ld": [],
                    "facebook_profile": {
                        "display_name": "Example Person",
                        "friends_count_text": "52",
                        "friends_text": "52 ami(e)s",
                        "followers_count_text": "1,2 K",
                        "bio": "Open source investigator",
                        "details": [
                            "Informations personnelles: Habite à Paris",
                            "Formation: Université Exemple",
                        ],
                        "external_links": ["https://example.org/profile"],
                        "profile_photo_url": (
                            "https://scontent.example/photo-id_n.jpg"
                            "?oh=volatile&oe=volatile"
                        ),
                        "profile_photo_identity": "photo-id_n.jpg",
                        "cover_photo_url": (
                            "https://scontent.example/cover-id_n.jpg"
                            "?oh=volatile&oe=volatile"
                        ),
                        "cover_photo_identity": "cover-id_n.jpg",
                        "loaded_post_count": 7,
                        "latest_post": {
                            "id": "pfbid-example",
                            "date": "21 juillet 2026, 19:37",
                            "content": "Example publication content",
                            "content_truncated": False,
                            "permalink": (
                                "https://www.facebook.com/permalink.php"
                                "?story_fbid=pfbid-example&id=123"
                            ),
                            "position": 1,
                            "pinned": False,
                        },
                    },
                },
                "custom_metrics": {},
            },
            (
                "page_name",
                "display_name",
                "friends_count",
                "followers",
                "bio",
                "profile_details",
                "profile_photo",
                "cover_photo",
                "external_links",
                "latest_post_id",
                "latest_post_date",
                "latest_post_content",
                "latest_post_permalink",
            ),
        )

        self.assertEqual(result.metrics["page_name"]["value"], "Example Person")
        self.assertEqual(
            result.metrics["display_name"]["value"],
            "Example Person",
        )
        self.assertEqual(result.metrics["friends_count"]["value"], 52)
        self.assertEqual(result.metrics["followers"]["value"], 1_200)
        self.assertEqual(result.metrics["followers"]["precision"], "rounded")
        self.assertEqual(
            result.metrics["bio"]["value"],
            "Open source investigator",
        )
        self.assertEqual(
            result.metrics["profile_details"]["value"],
            [
                "Informations personnelles: Habite à Paris",
                "Formation: Université Exemple",
            ],
        )
        self.assertEqual(
            result.metrics["profile_photo"]["comparison_key"],
            "photo-id_n.jpg",
        )
        self.assertEqual(
            result.metrics["cover_photo"]["comparison_key"],
            "cover-id_n.jpg",
        )
        self.assertEqual(
            result.metrics["external_links"]["value"],
            ["https://example.org/profile"],
        )
        self.assertEqual(
            result.metrics["latest_post_id"]["value"],
            "pfbid-example",
        )
        self.assertEqual(
            result.metrics["latest_post_date"]["comparison_key"],
            "pfbid-example",
        )
        self.assertEqual(
            result.metrics["latest_post_content"]["value"],
            "Example publication content",
        )
        self.assertEqual(result.errors, [])

    async def test_facebook_snapshot_uses_semantic_dom_anchors(self):
        class SnapshotTab:
            def __init__(self):
                self.script = ""

            async def evaluate(self, script):
                self.script = script
                return {"signals": {}, "metadata": {}}

        tab = SnapshotTab()
        await social_profile_snapshot(
            tab,
            "facebook_page",
            ("latest_post_content", "friends_count"),
            {},
        )

        self.assertIn('data-ad-preview="message"', tab.script)
        self.assertIn("aria-posinset", tab.script)
        self.assertIn("sk=friends", tab.script)
        self.assertIn("profile photo|photo de profil", tab.script)
        self.assertIn("profileCoverPhoto", tab.script)
        self.assertIn("informations personnelles", tab.script)
        self.assertIn("mutualCountPattern", tab.script)
        self.assertIn("en\\s+commun|ami", tab.script)
        self.assertIn('getAttribute?.("xlink:href")', tab.script)
        self.assertIn('messageRaw[midpoint] === " "', tab.script)
        self.assertNotIn("x9f619", tab.script)

    def test_dom_parser_reports_selector_miss_without_zero(self):
        adapter = SocialAdapterRegistry().get("facebook_page")

        result = adapter.extract_dom(
            {
                "metadata": {},
                "signals": {
                    "og_title": "Example page | Facebook",
                    "og_description": "",
                    "links": [],
                    "labeled_texts": [],
                    "body_text": "No public counter is rendered.",
                    "json_ld": [],
                },
                "custom_metrics": {},
            },
            ("page_name", "followers", "likes"),
        )

        self.assertEqual(result.metrics["followers"]["status"], "missing")
        self.assertIsNone(result.metrics["followers"]["value"])
        self.assertEqual(
            result.metrics["followers"]["provenance"]["source"],
            "dom",
        )
        self.assertIn(
            "selector_miss",
            {error["code"] for error in result.errors},
        )

    async def test_api_failure_is_safe_and_leaves_dom_fallback_possible(self):
        secret = "secret-that-must-not-leak"
        registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(x_bearer_token=secret),
            http_client=_SocialHttpClient(
                [
                    SocialApiRequestError(
                        "api_http_error",
                        "Social API returned HTTP 403.",
                    )
                ]
            ),
        )

        result = await registry.get("x_profile").extract_api(
            "https://x.com/example",
            ("followers", "posts"),
        )

        self.assertEqual(result.metrics, {})
        self.assertEqual(result.errors[0]["code"], "api_http_error")
        self.assertNotIn(secret, repr(result))
        self.assertNotIn(secret, str(result.errors))


class _ProbeBrowser(FakeBrowser):
    def __init__(self, response):
        super().__init__()
        self.response = response

    def new_tab(self, url: str = "about:blank"):
        tab = super().new_tab(url)

        def evaluate(script: str):
            if "synthesixMonitorNavigationState" in script:
                return {
                    "marker": "synthesixMonitorNavigationState",
                    "final_url": url,
                    "ready_state": "complete",
                    "has_body": True,
                }
            if isinstance(self.response, BaseException):
                raise self.response
            return self.response

        tab.on("evaluate", evaluate)
        return tab


class PageMonitorProbeTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        repository = InvestigationRepository(
            Path(self.temp_dir.name) / "monitoring.db"
        )
        self.service = InvestigationService(repository)
        self.service.initialize()
        investigation = self.service.create({"title": "Probe case"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/watch",
                "title": "Watched page",
                "description": "",
                "referrer": "",
            },
        )
        self.investigation_id = investigation.id
        self.monitor = self.service.create_page_monitor(
            investigation.id,
            saved.id,
            {
                "mode": "custom",
                "profile": "generic_page",
                "metrics": ["title", "price", "availability"],
                "selectors": {
                    "price": "[data-price]",
                    "availability": "[data-stock]",
                },
                "check_interval_minutes": 60,
            },
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_social_monitor(
        self,
        url,
        profile,
        metrics,
        *,
        selectors=None,
    ):
        saved = self.service.save_page(
            self.investigation_id,
            {
                "url": url,
                "title": f"{profile} page",
                "description": "",
                "referrer": "",
            },
        )
        return self.service.create_page_monitor(
            self.investigation_id,
            saved.id,
            {
                "mode": "custom",
                "profile": profile,
                "metrics": metrics,
                "selectors": selectors or {},
                "check_interval_minutes": 60,
            },
        )

    async def test_probe_records_partial_snapshot_without_heavy_artifacts(self):
        browser = _ProbeBrowser(
            {
                "final_url": "https://example.org/watch?resolved=1",
                "metadata": {
                    "ready_state": "interactive",
                    "language": "fr",
                    "canonical_url": "https://example.org/watch",
                    "content_type": "text/html",
                },
                "metrics": {
                    "title": {
                        "status": "ok",
                        "kind": "text",
                        "value": "  Watched   page  ",
                    },
                    "price": {
                        "status": "ok",
                        "kind": "number",
                        "value": 125,
                    },
                    "availability": {
                        "status": "missing",
                        "kind": "state",
                        "value": None,
                    },
                },
                "errors": [],
                "diagnostics": {
                    "requested_metrics": 3,
                    "ok_metrics": 2,
                    "missing_metrics": 1,
                },
            }
        )
        probe = PageMonitorProbe(BrowserService(browser), self.service)

        result = await probe.run(
            self.investigation_id,
            self.monitor.id,
        )

        observation = result.observation
        self.assertEqual(observation.status, "partial")
        self.assertEqual(observation.change_status, "baseline")
        self.assertFalse(result.archive_recommended)
        self.assertEqual(
            observation.final_url,
            "https://example.org/watch?resolved=1",
        )
        self.assertEqual(observation.metrics["title"]["value"], "Watched page")
        self.assertEqual(
            observation.metrics["availability"]["status"],
            "missing",
        )
        self.assertEqual(browser.journal.count("evaluate"), 2)
        self.assertEqual(browser.journal.count("send"), 0)
        self.assertEqual(browser.journal.count("save_screenshot"), 0)
        self.assertEqual(browser.journal.count("close"), 1)

    async def test_probe_recommends_archive_for_significant_change(self):
        baseline_browser = _ProbeBrowser(
            {
                "final_url": "https://example.org/watch",
                "metadata": {"ready_state": "complete"},
                "metrics": {
                    "title": {
                        "status": "ok",
                        "kind": "text",
                        "value": "Original page",
                    },
                    "price": {
                        "status": "ok",
                        "kind": "number",
                        "value": 100,
                    },
                    "availability": {
                        "status": "ok",
                        "kind": "state",
                        "value": True,
                    },
                },
                "errors": [],
                "diagnostics": {},
            }
        )
        await PageMonitorProbe(
            BrowserService(baseline_browser),
            self.service,
        ).run(self.investigation_id, self.monitor.id)
        changed_browser = _ProbeBrowser(
            {
                "final_url": "https://example.org/watch",
                "metadata": {"ready_state": "complete"},
                "metrics": {
                    "title": {
                        "status": "ok",
                        "kind": "text",
                        "value": "Completely different content",
                    },
                    "price": {
                        "status": "ok",
                        "kind": "number",
                        "value": 150,
                    },
                    "availability": {
                        "status": "ok",
                        "kind": "state",
                        "value": False,
                    },
                },
                "errors": [],
                "diagnostics": {},
            }
        )

        result = await PageMonitorProbe(
            BrowserService(changed_browser),
            self.service,
        ).run(self.investigation_id, self.monitor.id)

        self.assertTrue(result.archive_recommended)
        self.assertEqual(result.observation.change_status, "changed")
        refreshed = self.service.get_page_monitor(
            self.investigation_id,
            self.monitor.id,
        )
        self.assertEqual(refreshed.check_status, "changed")
        self.assertIsNotNone(refreshed.next_check_at)

    async def test_probe_failure_records_error_and_closes_tab(self):
        browser = _ProbeBrowser(RuntimeError("document detached"))

        result = await PageMonitorProbe(
            BrowserService(browser),
            self.service,
        ).run(self.investigation_id, self.monitor.id)

        self.assertEqual(result.observation.status, "error")
        self.assertEqual(result.observation.change_status, "error")
        self.assertEqual(
            result.observation.metrics["price"]["status"],
            "error",
        )
        self.assertEqual(result.observation.errors[0]["code"], "probe_failed")
        self.assertEqual(browser.journal.count("close"), 1)
        refreshed = self.service.get_page_monitor(
            self.investigation_id,
            self.monitor.id,
        )
        self.assertEqual(refreshed.check_status, "error")
        self.assertEqual(refreshed.consecutive_failures, 1)

    async def test_probe_marks_authentication_page_as_explicit_error(self):
        browser = _ProbeBrowser(
            {
                "final_url": "https://example.org/login",
                "metadata": {
                    "ready_state": "complete",
                    "blocking_reason": "authentication_required",
                },
                "metrics": {
                    "title": {
                        "status": "ok",
                        "kind": "text",
                        "value": "Sign in",
                    },
                    "price": {
                        "status": "unavailable",
                        "kind": "text",
                        "value": None,
                    },
                    "availability": {
                        "status": "unavailable",
                        "kind": "text",
                        "value": None,
                    },
                },
                "errors": [],
                "diagnostics": {},
            }
        )

        result = await PageMonitorProbe(
            BrowserService(browser),
            self.service,
        ).run(self.investigation_id, self.monitor.id)

        self.assertEqual(result.observation.status, "error")
        self.assertEqual(
            result.observation.errors[0]["code"],
            "authentication_required",
        )
        self.assertFalse(result.archive_recommended)

    async def test_paused_monitor_is_not_opened(self):
        paused = self.service.update_page_monitor_configuration(
            self.investigation_id,
            self.monitor.id,
            {
                "mode": "custom",
                "profile": "generic_page",
                "metrics": ["title"],
                "is_enabled": False,
            },
        )
        browser = _ProbeBrowser({})

        with self.assertRaisesRegex(
            InvestigationValidationError,
            "Paused page monitors",
        ):
            await PageMonitorProbe(
                BrowserService(browser),
                self.service,
            ).run(self.investigation_id, paused.id)

        self.assertEqual(browser.journal.count("browser.get"), 0)

    async def test_social_api_complete_probe_does_not_open_browser(self):
        monitor = self._create_social_monitor(
            "https://youtube.com/@example",
            "youtube_channel",
            [
                "channel_name",
                "description",
                "subscribers",
                "videos",
                "views",
            ],
        )
        browser = _ProbeBrowser({})
        registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(
                youtube_api_key="youtube-secret",
            ),
            http_client=_SocialHttpClient(
                [
                    {
                        "items": [
                            {
                                "snippet": {
                                    "title": "Example channel",
                                    "description": "Description",
                                },
                                "statistics": {
                                    "subscriberCount": "123000",
                                    "hiddenSubscriberCount": False,
                                    "videoCount": "20",
                                    "viewCount": "5000",
                                },
                            }
                        ]
                    }
                ]
            ),
        )

        result = await PageMonitorProbe(
            BrowserService(browser),
            self.service,
            social_registry=registry,
        ).run(self.investigation_id, monitor.id)

        self.assertEqual(result.observation.status, "ok")
        self.assertEqual(browser.journal.count("browser.get"), 0)
        self.assertEqual(
            result.observation.metrics["subscribers"]["precision"],
            "rounded",
        )
        self.assertEqual(
            result.observation.metrics["subscribers"]["provenance"][
                "source"
            ],
            "api",
        )
        self.assertEqual(
            result.observation.metadata["social_adapter"]["attempts"][0][
                "status"
            ],
            "ok",
        )
        self.assertNotIn(
            "youtube-secret",
            repr(result.observation.to_payload()),
        )

    async def test_social_api_failure_falls_back_to_dom_per_metric(self):
        monitor = self._create_social_monitor(
            "https://x.com/example",
            "x_profile",
            ["profile_name", "followers", "posts"],
        )
        browser = _ProbeBrowser(
            {
                "final_url": "https://x.com/example",
                "metadata": {
                    "ready_state": "complete",
                    "language": "en",
                    "blocking_reason": "",
                },
                "custom_metrics": {},
                "signals": {
                    "og_title": "Example (@example) / X",
                    "og_description": "",
                    "links": [],
                    "labeled_texts": [
                        "1,234 Followers",
                        "56 Posts",
                    ],
                    "body_text": "",
                    "json_ld": [],
                },
                "errors": [],
                "diagnostics": {},
            }
        )
        secret = "x-secret"
        registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(x_bearer_token=secret),
            http_client=_SocialHttpClient(
                [
                    SocialApiRequestError(
                        "api_http_error",
                        "Social API returned HTTP 403.",
                    )
                ]
            ),
        )

        result = await PageMonitorProbe(
            BrowserService(browser),
            self.service,
            social_registry=registry,
        ).run(self.investigation_id, monitor.id)

        self.assertEqual(result.observation.status, "ok")
        self.assertEqual(
            result.observation.metrics["followers"]["value"],
            1234,
        )
        self.assertEqual(
            result.observation.metrics["followers"]["provenance"]["source"],
            "dom",
        )
        self.assertIn(
            "api_http_error",
            {error["code"] for error in result.observation.errors},
        )
        self.assertEqual(browser.journal.count("evaluate"), 2)
        self.assertEqual(browser.journal.count("close"), 1)
        self.assertNotIn(
            secret,
            repr(result.observation.to_payload()),
        )

    async def test_social_custom_selector_overrides_api_metric(self):
        monitor = self._create_social_monitor(
            "https://x.com/example",
            "x_profile",
            ["followers"],
            selectors={"followers": "[data-followers]"},
        )
        browser = _ProbeBrowser(
            {
                "final_url": "https://x.com/example",
                "metadata": {
                    "ready_state": "complete",
                    "blocking_reason": "",
                },
                "custom_metrics": {
                    "followers": {
                        "status": "ok",
                        "kind": "number",
                        "value": 222,
                    }
                },
                "signals": {
                    "links": [],
                    "labeled_texts": [],
                    "body_text": "",
                    "json_ld": [],
                },
                "errors": [],
                "diagnostics": {},
            }
        )
        registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(x_bearer_token="x-secret"),
            http_client=_SocialHttpClient(
                [
                    {
                        "data": {
                            "name": "Example",
                            "description": "",
                            "entities": {},
                            "public_metrics": {
                                "followers_count": 111,
                            },
                        }
                    }
                ]
            ),
        )

        result = await PageMonitorProbe(
            BrowserService(browser),
            self.service,
            social_registry=registry,
        ).run(self.investigation_id, monitor.id)

        self.assertEqual(
            result.observation.metrics["followers"]["value"],
            222,
        )
        self.assertEqual(
            result.observation.metrics["followers"]["provenance"]["source"],
            "dom",
        )
        self.assertEqual(
            result.observation.metrics["followers"]["provenance"]["field"],
            "selector:followers",
        )

    async def test_hidden_youtube_count_survives_empty_dom_fallback(self):
        monitor = self._create_social_monitor(
            "https://youtube.com/@example",
            "youtube_channel",
            ["subscribers"],
        )
        browser = _ProbeBrowser(
            {
                "final_url": "https://youtube.com/@example",
                "metadata": {
                    "ready_state": "complete",
                    "blocking_reason": "",
                },
                "custom_metrics": {},
                "signals": {
                    "links": [],
                    "labeled_texts": [],
                    "body_text": "Subscribers are hidden.",
                    "json_ld": [],
                },
                "errors": [],
                "diagnostics": {},
            }
        )
        registry = SocialAdapterRegistry(
            credentials=SocialApiCredentials(
                youtube_api_key="youtube-secret",
            ),
            http_client=_SocialHttpClient(
                [
                    {
                        "items": [
                            {
                                "snippet": {},
                                "statistics": {
                                    "hiddenSubscriberCount": True,
                                },
                            }
                        ]
                    }
                ]
            ),
        )

        result = await PageMonitorProbe(
            BrowserService(browser),
            self.service,
            social_registry=registry,
        ).run(self.investigation_id, monitor.id)

        metric = result.observation.metrics["subscribers"]
        self.assertEqual(metric["status"], "missing")
        self.assertEqual(metric["precision"], "hidden")
        self.assertEqual(metric["provenance"]["source"], "api")


class _SchedulerProbe:
    def __init__(self, service, behaviors):
        self.service = service
        self.behaviors = {
            monitor_id: list(items)
            for monitor_id, items in behaviors.items()
        }
        self.calls = {}
        self.active = 0
        self.max_active = 0

    async def run(self, investigation_id, monitor_id):
        self.calls[monitor_id] = self.calls.get(monitor_id, 0) + 1
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0.01)
            behavior = self.behaviors[monitor_id].pop(0)
            if isinstance(behavior, BaseException):
                raise behavior
            previous = self.service.get_latest_page_monitor_observation(
                investigation_id,
                monitor_id,
            )
            status = behavior.get("status", "ok")
            archive_recommended = bool(
                behavior.get("archive_recommended", False)
            )
            errors = list(behavior.get("errors", []))
            observation = self.service.record_page_monitor_observation(
                investigation_id,
                monitor_id,
                previous_observation_id=(
                    previous.id if previous is not None else None
                ),
                schema_version=1,
                observed_at=datetime.now(timezone.utc).isoformat(
                    timespec="microseconds"
                ),
                final_url="https://example.org/final",
                duration_ms=10,
                status=status,
                content_sha256="a" * 64,
                metadata={"profile": "generic_page"},
                metrics={
                    "title": {
                        "status": "error" if status == "error" else "ok",
                        "kind": "text",
                        "value": None if status == "error" else "Page",
                    }
                },
                errors=errors,
                changes=(
                    {"title": {"status": "changed", "kind": "text"}}
                    if archive_recommended
                    else {}
                ),
                change_status=(
                    "error"
                    if status == "error"
                    else "changed"
                    if archive_recommended
                    else "baseline"
                    if previous is None
                    else "unchanged"
                ),
                archive_recommended=archive_recommended,
            )
            return ProbeResult(observation=observation)
        finally:
            self.active -= 1


class PageMonitorSchedulerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        repository = InvestigationRepository(
            Path(self.temp_dir.name) / "scheduler.db"
        )
        self.service = InvestigationService(repository)
        self.service.initialize()
        self.investigation = self.service.create(
            {"title": "Scheduler case"}
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_monitor(
        self,
        suffix,
        *,
        archive_policy="on_change",
    ):
        saved = self.service.save_page(
            self.investigation.id,
            {
                "url": f"https://example.org/{suffix}",
                "title": f"Page {suffix}",
                "description": "",
                "referrer": "",
            },
        )
        return self.service.create_page_monitor(
            self.investigation.id,
            saved.id,
            {
                "metrics": ["title"],
                "archive_policy": archive_policy,
                "check_interval_minutes": 60,
            },
        )

    async def test_atomic_claim_prevents_two_workers_from_sharing_monitor(self):
        monitor = self._create_monitor("atomic")
        due_at = "2026-07-16T18:00:00.000000+00:00"

        first = await asyncio.to_thread(
            self.service.claim_due_page_monitors,
            "worker-a",
            due_at=due_at,
            limit=1,
            lease_seconds=5,
        )
        second = await asyncio.to_thread(
            self.service.claim_due_page_monitors,
            "worker-b",
            due_at=due_at,
            limit=1,
            lease_seconds=5,
        )

        self.assertEqual([item.id for item in first], [monitor.id])
        self.assertEqual(second, [])
        claimed = self.service.get_page_monitor(
            self.investigation.id,
            monitor.id,
        )
        self.assertEqual(claimed.lease_owner, "worker-a")

        expired = await asyncio.to_thread(
            self.service.claim_due_page_monitors,
            "worker-b",
            due_at="2026-07-16T18:00:06.000000+00:00",
            limit=1,
            lease_seconds=5,
        )
        self.assertEqual([item.id for item in expired], [monitor.id])

    async def test_scheduler_limits_concurrency_retries_and_isolates_failures(self):
        retrying = self._create_monitor("retrying")
        partial = self._create_monitor("partial")
        failing = self._create_monitor("failing")
        probe = _SchedulerProbe(
            self.service,
            {
                retrying.id: [RuntimeError("detached"), {"status": "ok"}],
                partial.id: [{"status": "partial"}],
                failing.id: [RuntimeError("offline"), RuntimeError("offline")],
            },
        )
        scheduler = PageMonitorScheduler(
            self.service,
            probe,
            options=MonitorSchedulerOptions(
                poll_interval=1,
                batch_size=3,
                concurrency=2,
                lease_seconds=5,
                attempt_timeout=1,
                retry_attempts=1,
                retry_delay=0,
                jitter_seconds=0,
                failure_backoff_seconds=30,
                max_failures=3,
            ),
            worker_id="scheduler-test",
        )

        summary = await scheduler.run_once()

        self.assertEqual(summary.claimed, 3)
        self.assertEqual(summary.succeeded, 1)
        self.assertEqual(summary.partial, 1)
        self.assertEqual(summary.failed, 1)
        self.assertEqual(probe.calls[retrying.id], 2)
        self.assertEqual(probe.calls[failing.id], 2)
        self.assertLessEqual(probe.max_active, 2)
        failed = self.service.get_page_monitor(
            self.investigation.id,
            failing.id,
        )
        self.assertEqual(failed.consecutive_failures, 1)
        self.assertIsNotNone(failed.next_check_at)
        self.assertIsNone(failed.lease_owner)

    async def test_scheduler_runs_one_monitor_immediately_and_respects_pause(self):
        monitor = self._create_monitor("manual")
        probe = _SchedulerProbe(
            self.service,
            {monitor.id: [{"status": "ok"}]},
        )
        scheduler = PageMonitorScheduler(
            self.service,
            probe,
            options=MonitorSchedulerOptions(
                poll_interval=60,
                batch_size=2,
                concurrency=1,
                lease_seconds=5,
                attempt_timeout=1,
                retry_attempts=0,
                jitter_seconds=0,
            ),
            worker_id="manual-test",
        )

        summary = await scheduler.run_monitor_now(
            self.investigation.id,
            monitor.id,
        )

        self.assertEqual(summary.claimed, 1)
        self.assertEqual(summary.succeeded, 1)
        self.assertEqual(probe.calls[monitor.id], 1)
        refreshed = self.service.get_page_monitor(
            self.investigation.id,
            monitor.id,
        )
        self.assertIsNone(refreshed.lease_owner)
        self.assertIsNotNone(refreshed.next_check_at)

        paused = self.service.update_page_monitor_configuration(
            self.investigation.id,
            monitor.id,
            {
                "mode": refreshed.monitor_mode,
                "profile": refreshed.monitor_profile,
                "metrics": refreshed.monitor_config["metrics"],
                "selectors": refreshed.monitor_config["selectors"],
                "archive_policy": refreshed.monitor_config["archive_policy"],
                "check_interval_minutes": refreshed.check_interval_minutes,
                "is_enabled": False,
            },
        )
        self.assertFalse(paused.is_enabled)
        with self.assertRaisesRegex(
            InvestigationValidationError,
            "Resume this page monitor",
        ):
            await scheduler.run_monitor_now(
                self.investigation.id,
                monitor.id,
            )

    async def test_scheduler_applies_archive_policy_and_pauses_intervention(self):
        archived_monitor = self._create_monitor(
            "archive",
            archive_policy="on_change",
        )
        no_archive_monitor = self._create_monitor(
            "no-archive",
            archive_policy="never",
        )
        challenge_monitor = self._create_monitor("challenge")
        probe = _SchedulerProbe(
            self.service,
            {
                archived_monitor.id: [
                    {"status": "ok", "archive_recommended": True}
                ],
                no_archive_monitor.id: [
                    {"status": "ok", "archive_recommended": True}
                ],
                challenge_monitor.id: [
                    {
                        "status": "error",
                        "errors": [
                            {
                                "metric": "",
                                "code": "authentication_required",
                                "message": "Sign in",
                            }
                        ],
                    }
                ],
            },
        )
        archived_ids = []

        async def archive_handler(monitor, _result):
            archived_ids.append(monitor.id)

        scheduler = PageMonitorScheduler(
            self.service,
            probe,
            options=MonitorSchedulerOptions(
                poll_interval=1,
                batch_size=3,
                concurrency=2,
                lease_seconds=5,
                attempt_timeout=1,
                retry_attempts=1,
                retry_delay=0,
                jitter_seconds=0,
                max_failures=5,
            ),
            archive_handler=archive_handler,
            worker_id="archive-test",
        )

        summary = await scheduler.run_once()

        self.assertEqual(summary.succeeded, 2)
        self.assertEqual(summary.failed, 1)
        self.assertEqual(summary.archived, 1)
        self.assertEqual(summary.paused, 1)
        self.assertEqual(archived_ids, [archived_monitor.id])
        paused = self.service.get_page_monitor(
            self.investigation.id,
            challenge_monitor.id,
        )
        self.assertFalse(paused.is_enabled)
        self.assertEqual(paused.check_status, "paused")
        self.assertIsNone(paused.next_check_at)


if __name__ == "__main__":
    unittest.main()
