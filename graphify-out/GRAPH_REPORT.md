# Graph Report - MSA  (2026-07-07)

## Corpus Check
- 104 files · ~117,406 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1795 nodes · 4635 edges · 89 communities (59 shown, 30 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 318 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9af012e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]

## God Nodes (most connected - your core abstractions)
1. `InvestigationRepository` - 108 edges
2. `InvestigationService` - 98 edges
3. `get_settings()` - 69 edges
4. `BraveSearchEngine` - 64 edges
5. `generate_investigation_page()` - 62 edges
6. `DuckDuckGoSearchEngine` - 61 edges
7. `FakeTab` - 59 edges
8. `SearchEngine` - 59 edges
9. `InvestigationValidationError` - 59 edges
10. `InvestigationRepositoryTestCase` - 57 edges

## Surprising Connections (you probably didn't know these)
- `BraveSearchEngine` --uses--> `RobotChallengeError`  [INFERRED]
  brave.py → exceptions.py
- `BraveSearchEngine` --uses--> `SearchEngine`  [INFERRED]
  brave.py → search_engine.py
- `SearchOrchestrator` --uses--> `BraveSearchEngine`  [INFERRED]
  search_orchestrator.py → brave.py
- `SearchRunResult` --uses--> `BraveSearchEngine`  [INFERRED]
  search_orchestrator.py → brave.py
- `BingPaginationTestCase` --uses--> `BraveSearchEngine`  [INFERRED]
  tests/test_engines.py → brave.py

## Import Cycles
- None detected.

## Communities (89 total, 30 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (59): Element, _add_graphml_data(), _append_property(), _best_coordinate_fact(), _build_curated_graph(), build_export_graph(), _capture_has_image(), _content_size() (+51 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (14): Base exception for application-level Synthesix failures., SynthesixError, add_context_to_breakdown(), build_relevance_explainer(), build_relevance_scorer(), calculate_relevance(), extract_scoring_terms(), Calcul relevance score      Args:         row (dict): row of the dataframe (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (13): InvestigationValidationError, Raised when investigation input does not satisfy application rules., LocalSearchFilters, _append_property_value(), _clean_text(), _default_property_key(), _extracted_property_key(), _extracted_property_value() (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (27): capture_html(), capture_mhtml(), capture_png(), CapturedDocument, CapturedPng, _is_sensitive_field(), normalize_html_text(), normalize_selection() (+19 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (15): ABC, Launch a search and return a DataFrame of results., Hand a pooled tab back to the pool; close tabs the pool does not own., Execute the search and return the results., Set the selector for the search engine.         Selector used as a reference poi, Construct the URL for the search., Parse the raw HTML and return a list of structured results., Return a dictionary with the XPaths necessary for parsing. (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (40): _append_match(), _clean_matched_value(), _date_value(), _digits(), EntityCandidate, extract_entity_candidates(), _extract_from_text(), _inferred_field_label() (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (21): UtilsTestCase, add_to_history(), _asset_prefix(), _brand_markup(), clear_synthesix_history(), generate_history_html(), generate_html_report(), _history_sort_key() (+13 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (31): _bookmark_folder(), _browser_types_to_try(), _build_zendriver_config(), _chrome_timestamp(), _clear_profile_browsing_data(), _ensure_flatpak_brave_wrapper(), _ensure_synthesix_bookmark(), _find_native_browser_executable() (+23 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (12): fake_clock(), FakeBrowser, FakeElement, Scriptable stand-in for ``zendriver.Browser`` (see module docstring)., Patch ``time.monotonic`` and ``asyncio.sleep`` inside ``modules``.      Only the, Minimal DOM node double (truthy, clickable)., CaptureExampleTestCase, EngineWaitExampleTestCase (+4 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (7): Any, FakeTab, Scriptable stand-in for ``zendriver.Tab`` (see module docstring)., Queue successive responses for ``method`` (FIFO)., Fallback handler called with the call's positional arguments., Mirror ``zendriver.core.connection.Connection.add_handler``., Invoke handlers registered for ``event_type`` with ``event``.          Awaits co

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (11): BrowserService, Browser-scoped CDP operations and per-target state.      One instance per live b, Page-target ids from zendriver's event-maintained registry., Cheap per-tick liveness signal (no CDP round-trip).          The event-maintaine, Authoritative `getTargets` round-trip: refresh the registry and         report t, Live page tabs, or ``None`` when the browser is unreachable.          Reads zend, Open ``url`` (new tab by default) and return the tab handle., Arm ``script`` to run before any page script on future         navigations of `` (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (11): BrowserSessionError, RobotChallengeError, SearchEngineError, DummySearchEngine, FailingBrowser, LoadedTab, SearchEngineErrorTestCase, WorkingBrowser (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (39): _compact_url(), _display_datetime(), _doc_kind_badge(), _dom_id_fragment(), _entity_rows_markup(), _entity_status_options(), _entity_type_options(), _evidence_markup() (+31 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (34): _asset_prefix(), _filter_summary(), generate_local_search_page(), _relative_href(), _result_card(), LocalSearchViewTestCase, chip(), context_bar() (+26 more)

### Community 15 - "Community 15"
Cohesion: 0.42
Nodes (4): EvidenceCapture, EvidenceCapture, _capture_datetime(), _has_archive_artifact()

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (18): date, build_display_query(), build_engine_date_params(), build_engine_query(), _date_range(), _domain_from_site_filter(), _link_matches_filetype(), _link_matches_site() (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.20
Nodes (28): AppSettings, EvidenceCaptureError, Raised when an evidence artifact cannot be captured or persisted., InvestigationService, _archive_page(), _archive_page_for_selection_source(), _artifact_file_path(), _cached_history_payload() (+20 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (5): DuckDuckGoSearchEngine, _create_duckduckgo_engine(), DuckDuckGoParsingTestCase, DuckDuckGoRobotChallengeErrorTestCase, T-012: a matching probe finishes the wait without shipping HTML.

### Community 19 - "Community 19"
Cohesion: 0.19
Nodes (22): applyLanguage(), applySettings(), applyThemeSetting(), broadcastSettings(), currentLanguage(), detectedLanguage(), init(), installDialogTranslations() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (15): apply_cli_runtime_overrides(), configure_event_loop_policy(), configure_logging(), _default_archive_name(), _default_capture_name(), _investigation_payload(), _log_level_from_args(), parse_cli_args() (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (8): BraveSearchEngine, Save the raw page once when Brave yields zero results, so its         current m, Construct the query for the search., Wait for Brave's client-rendered results, then read — same strategy         as, _create_brave_engine(), EngineGoldenParsingTestCase, BraveParsingTestCase, BraveRobotChallengeErrorTestCase

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (4): _attach_selection_to_graph_entity(), _create_graph_entity_from_selection(), _retry_search_combination(), InvestigationPageRoutingTestCase

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (4): generate_investigation_page(), Path, InvestigationViewTestCase, workspace_payload()

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (7): BraveEmptyResultsDumpTestCase, BraveResultsWaitTestCase, GoogleRobotCheckTestCase, _GoogleRobotTab, A silently empty Brave (both embedded-JSON and XPath parsing miss)     saves the, Brave renders results client-side after a reveal; the wait must hold     for the, T-004: captcha detection uses query_selector and the /sorry/ URL,     and an unr

### Community 28 - "Community 28"
Cohesion: 0.13
Nodes (11): _arm_overlay_focus_guard(), _install_and_consume_save_overlay(), _overlay_bundle_script(), _overlay_focus_guard_script(), _overlay_injection_blocked(), JS armed early (before any page script) so it wins the DOM event     ordering r, Register the focus-guard script for future navigations of ``tab``.      Best-e, Skip overlay injection on surfaces where it breaks or crashes Chrome.      Goo (+3 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (5): GraphEntity, HTMLElementTagNameMap, PROPERTY_TYPE_LABELS, HTMLElementTagNameMap, SxOverlaySelectionTrigger

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (15): compilerOptions, experimentalDecorators, isolatedModules, lib, module, moduleResolution, noEmit, noUnusedLocals (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (8): EvidenceArtifact, InvestigationSearchRun, PageComparison, PageMonitor, InvestigationSearchRun, PageComparison, PageMonitor, Row

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (14): dependencies, lit, description, devDependencies, esbuild, typescript, name, private (+6 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (21): eval_js(), Evaluate ``script`` on ``tab``, best-effort.      Counts one instrumented call u, _apply_settings_to_tabs(), _consume_home_tab_action(), _consume_page_tab_action(), _consume_settings_change(), _has_page_archive_artifact(), _is_external_web_tab() (+13 more)

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (3): HTMLElementTagNameMap, OverlayActionState, SxOverlayAction

### Community 38 - "Community 38"
Cohesion: 0.16
Nodes (10): _challenge_excerpt(), _html_to_visible_text(), looks_like_brave_challenge_url(), looks_like_brave_robot_challenge(), _normalize_challenge_text(), datetime, parse_with_xpath(), Parse generic search results from HTML using provided XPaths.     Args: (+2 more)

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (8): CATEGORY_COLORS, FALLBACK_PALETTE, GraphData, GraphEdge, GraphNode, HTMLElementTagNameMap, Link, Particle

### Community 40 - "Community 40"
Cohesion: 0.12
Nodes (7): CallJournal, CallRecord, _FakeCookies, _ModuleProxy, Fake Zendriver browser/tab harness shared by Synthesix tests (T-050).  Reference, Pass-through module wrapper overriding a handful of attributes., Timestamped log of every fake call, shared browser <-> tabs.

### Community 41 - "Community 41"
Cohesion: 0.21
Nodes (6): _dictionary_keys(), I18nCoverageTestCase, _numeric_patterns(), Guard tests keeping the cockpit redesign fully internationalized.  Generated p, Every visible home string (and translatable attribute) must resolve         to, multilingual (fr/es/zh) and additionalTranslations (pt/de) must hold         th

### Community 42 - "Community 42"
Cohesion: 0.17
Nodes (8): Window, CaptureAttach, CaptureScope, GraphEntity, HTMLElementTagNameMap, DragState, HTMLElementTagNameMap, OverlayActionElement

### Community 43 - "Community 43"
Cohesion: 0.14
Nodes (5): Brand, BRANDS, FAVICON_COLORS, HTMLElementTagNameMap, SxSavedPageCard

### Community 44 - "Community 44"
Cohesion: 0.12
Nodes (20): Declared zeroneurone PropertyType for a canonical tagset key, else ''., zeroneurone_property_type(), _default_entity_category(), _default_property_key(), _detection_title(), _entity_markup(), _entity_property_key(), _entity_property_type() (+12 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (6): _html_to_visible_text(), looks_like_duckduckgo_forbidden(), looks_like_duckduckgo_no_results(), looks_like_duckduckgo_robot_challenge(), True when DuckDuckGo explicitly reports an empty result set.      Used to stop w, DuckDuckGoNoResultsTestCase

### Community 46 - "Community 46"
Cohesion: 0.14
Nodes (6): DataFrame, Exception, aggregate_search_results(), SearchFilters, Semaphore, AggregateSearchResultsTestCase

### Community 48 - "Community 48"
Cohesion: 0.17
Nodes (18): Browser, get_browser_service(), Shared :class:`BrowserService` for ``browser`` (one per instance).      Browsers, _focus_or_open_home_tab(), _is_home_tab(), _normalize_tab_url(), _open_or_refresh_investigation_page(), _open_tabs() (+10 more)

### Community 49 - "Community 49"
Cohesion: 0.13
Nodes (5): GoogleSearchEngine, Best-effort: click the reCAPTCHA "I'm not a robot" checkbox with a         trust, _create_google_engine(), ProbePageStateTestCase, T-012: composite probe replaces per-iteration query_selector polls     and in-lo

### Community 51 - "Community 51"
Cohesion: 0.33
Nodes (5): assets, common, configs, root, watch

### Community 53 - "Community 53"
Cohesion: 0.13
Nodes (16): Connection, ExtractedEntity, InvestigationEntity, InvestigationResult, ExtractedEntity, InvestigationEntity, InvestigationResult, UrlAnalysis (+8 more)

### Community 56 - "Community 56"
Cohesion: 0.21
Nodes (5): SearchOrchestrator, FakeEngine, ReportCapture, SearchOrchestratorTestCase, SlowEngine

### Community 57 - "Community 57"
Cohesion: 0.21
Nodes (10): InvestigationError, InvestigationHasDataError, InvestigationNotFoundError, InvestigationResultNotFoundError, Base exception for investigation storage and workflow failures., SearchRunNotFoundError, LocalSearchResult, canonicalize_url() (+2 more)

### Community 60 - "Community 60"
Cohesion: 0.36
Nodes (5): normalize_query_variants(), suggest_query_variants(), _without_accents(), QueryVariantsTestCase, is_advanced_query()

### Community 61 - "Community 61"
Cohesion: 0.12
Nodes (8): HTMLElementTagNameMap, SxChip, HTMLElementTagNameMap, SxExportCard, GroupingRule, HTMLElementTagNameMap, HTMLElementTagNameMap, SxProvenance

### Community 62 - "Community 62"
Cohesion: 0.25
Nodes (3): maybe_log_snapshot(), Process-wide counters for CDP traffic (T-006).  Categories used across the codeb, Log a rate summary at DEBUG level, at most once per ``interval``.

### Community 64 - "Community 64"
Cohesion: 0.22
Nodes (10): _archive_artifact(), _archive_href(), _capture_open_href(), _graph_entities_markup(), _has_archive_artifact(), _imported_doc_kind(), _protected_capture_ids(), Coarse file-type key (image/pdf/audio/video/document/file) for an     imported (+2 more)

### Community 66 - "Community 66"
Cohesion: 0.16
Nodes (6): BingSearchEngine, Resolve a Bing ``/ck/a`` redirect to the real destination URL.      Bing wraps, resolve_bing_redirect(), _create_bing_engine(), BingPaginationTestCase, BingRedirectTestCase

### Community 69 - "Community 69"
Cohesion: 0.18
Nodes (11): Single entry point for Zendriver/CDP access (T-020)., click_at(), mhtml(), outer_html(), Thin single layer over Zendriver/CDP (T-020).  Every CDP exchange initiated by t, Dispatch a trusted left-click at viewport coordinates ``(x, y)``.      Unlike a, Capture a PNG of the ``clip`` viewport region, returned as bytes.      Exception, Return the full MHTML snapshot of the page. Exceptions propagate. (+3 more)

### Community 75 - "Community 75"
Cohesion: 0.12
Nodes (7): SearchEngine, FlakyParsePooledEngine, HangingTabEngine, PooledStubEngine, First variant fails at parse time, later variants succeed., Real SearchEngine subclass that opens a tab then hangs forever.      Exercises t, Real SearchEngine subclass exercising the T-014 tab pool end to end.

### Community 76 - "Community 76"
Cohesion: 0.35
Nodes (6): _build_country_index(), build_engine_region_params(), CountryRegion, _normalize_country_name(), resolve_country(), SearchRegionsTestCase

### Community 77 - "Community 77"
Cohesion: 0.19
Nodes (9): _log_search_task_outcome(), Run a search concurrently with the action loop (T-011).      The done callback, Background home search; owns the final home statuses., _run_search_action(), _search_task_running(), _start_search_task(), Task, BackgroundSearchTaskTestCase (+1 more)

### Community 80 - "Community 80"
Cohesion: 0.29
Nodes (3): PushTransportTestCase, T-021: push transport for local pages (home, investigation/report tabs).  `wait_, _ready_state()

### Community 82 - "Community 82"
Cohesion: 0.29
Nodes (3): EngineTabPool, One reusable tab per engine for a whole search run (T-014).      Query variants, Tab

### Community 83 - "Community 83"
Cohesion: 0.29
Nodes (3): CdpBudgetTestCase, make_tab(), FakeTab answering the home/overlay/page poll scripts (T-050 harness).

## Knowledge Gaps
- **74 isolated node(s):** `Window`, `CaptureScope`, `GraphEntity`, `CaptureAttach`, `HTMLElementTagNameMap` (+69 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 8` to `Community 1`, `Community 35`, `Community 4`, `Community 38`, `Community 7`, `Community 12`, `Community 45`, `Community 48`, `Community 17`, `Community 18`, `Community 83`, `Community 22`, `Community 23`, `Community 56`, `Community 25`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `InvestigationService` connect `Community 2` to `Community 32`, `Community 35`, `Community 5`, `Community 70`, `Community 6`, `Community 15`, `Community 48`, `Community 17`, `Community 53`, `Community 22`, `Community 24`, `Community 57`, `Community 58`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `BrowserService` connect `Community 11` to `Community 35`, `Community 69`, `Community 8`, `Community 48`, `Community 22`, `Community 28`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `Path` (e.g. with `.test_dumps_even_when_page_mentions_robot()` and `.test_dumps_only_once_per_search()`) actually correct?**
  _`Path` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `InvestigationRepository` (e.g. with `InvestigationHasDataError` and `InvestigationNotFoundError`) actually correct?**
  _`InvestigationRepository` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `InvestigationService` (e.g. with `InvestigationValidationError` and `EvidenceCapture`) actually correct?**
  _`InvestigationService` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `BraveSearchEngine` (e.g. with `RobotChallengeError` and `SearchEngine`) actually correct?**
  _`BraveSearchEngine` has 24 INFERRED edges - model-reasoned connections that need verification._