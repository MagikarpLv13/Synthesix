# Graph Report - MSA  (2026-07-09)

## Corpus Check
- 112 files · ~128,377 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2013 nodes · 5196 edges · 99 communities (67 shown, 32 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 369 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bdfd6962`
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
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]

## God Nodes (most connected - your core abstractions)
1. `InvestigationRepository` - 108 edges
2. `InvestigationService` - 98 edges
3. `get_settings()` - 85 edges
4. `BrowserService` - 70 edges
5. `BraveSearchEngine` - 64 edges
6. `DuckDuckGoSearchEngine` - 62 edges
7. `generate_investigation_page()` - 62 edges
8. `main()` - 61 edges
9. `FakeTab` - 59 edges
10. `SearchEngine` - 59 edges

## Surprising Connections (you probably didn't know these)
- `SearchBrowserProvider` --uses--> `HeadlessBrowserManager`  [INFERRED]
  main.py → browser_manager.py
- `SearchBrowserProvider` --uses--> `AppSettings`  [INFERRED]
  main.py → settings.py
- `ActiveEngineTabSkipTestCase` --uses--> `SearchBrowserProvider`  [INFERRED]
  tests/test_main.py → main.py
- `ExtensionOverlayContextTestCase` --uses--> `SearchBrowserProvider`  [INFERRED]
  tests/test_main.py → main.py
- `HomeHistoryCacheTestCase` --uses--> `SearchBrowserProvider`  [INFERRED]
  tests/test_main.py → main.py

## Import Cycles
- None detected.

## Communities (99 total, 32 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (59): Element, _add_graphml_data(), _append_property(), _best_coordinate_fact(), _build_curated_graph(), build_export_graph(), _capture_has_image(), _content_size() (+51 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (13): add_context_to_breakdown(), build_relevance_explainer(), build_relevance_scorer(), calculate_relevance(), extract_scoring_terms(), Calcul relevance score      Args:         row (dict): row of the dataframe, ScoreBreakdown, ScoreComponent (+5 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (11): InvestigationValidationError, Raised when investigation input does not satisfy application rules., _append_property_value(), _clean_text(), _default_property_key(), _extracted_property_key(), _extracted_property_value(), InvestigationService (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (26): capture_html(), capture_mhtml(), capture_png(), CapturedDocument, CapturedPng, _is_sensitive_field(), normalize_html_text(), normalize_selection() (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (16): Launch a search and return a DataFrame of results., Hand a pooled tab back to the pool; close tabs the pool does not own., Execute the search and return the results., Set the selector for the search engine.         Selector used as a reference poi, Construct the URL for the search., Parse the raw HTML and return a list of structured results., Return a dictionary with the XPaths necessary for parsing., Per-engine markers consumed by :meth:`probe_page_state`.          Optional keys: (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (40): _append_match(), _clean_matched_value(), _date_value(), _digits(), EntityCandidate, extract_entity_candidates(), _extract_from_text(), _inferred_field_label() (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (20): datetime, UtilsTestCase, add_to_history(), _asset_prefix(), _brand_markup(), clear_synthesix_history(), generate_history_html(), generate_html_report() (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (64): _bookmark_folder(), _browser_types_to_try(), _build_zendriver_config(), _chrome_timestamp(), clear_browser_profile_data(), _clear_profile_browsing_data(), _configure_extension_launch(), detect_synthesix_extension() (+56 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (8): fake_clock(), FakeClock, FakeElement, Injectable monotonic clock; ``sleep`` advances it without real time., Patch ``time.monotonic`` and ``asyncio.sleep`` inside ``modules``.      Only the, Minimal DOM node double (truthy, clickable)., EngineWaitExampleTestCase, ProbeEngine

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (8): Any, FakeTab, Scriptable stand-in for ``zendriver.Tab`` (see module docstring)., Queue successive responses for ``method`` (FIFO)., Fallback handler called with the call's positional arguments., Mirror ``zendriver.core.connection.Connection.add_handler``., Invoke handlers registered for ``event_type`` with ``event``.          Awaits co, CaptureExampleTestCase

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (8): BrowserService, Browser-scoped CDP operations and per-target state.      One instance per live b, Open ``url`` (new tab by default) and return the tab handle., Arm ``script`` to run before any page script on future         navigations of ``, Register ``handler`` for a CDP event on ``tab`` (zendriver         ``add_handler, BrowserServiceTestCase, FakeWorkerConnection, Extension service-worker CDP connection double.      Answers the revision probe

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (5): build_evidence_manifest(), _attach_selection_to_graph_entity(), _capture_evidence(), _create_graph_entity_from_selection(), InvestigationPageRoutingTestCase

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (54): Declared zeroneurone PropertyType for a canonical tagset key, else ''., zeroneurone_property_type(), _archive_artifact(), _archive_href(), _default_entity_category(), _default_property_key(), _display_datetime(), _doc_kind_badge() (+46 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (28): chip(), context_bar(), domain_of(), empty_state(), esc(), _highlight(), icon(), insight_grid() (+20 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (15): InvestigationError, InvestigationHasDataError, InvestigationNotFoundError, InvestigationResultNotFoundError, Base exception for investigation storage and workflow failures., SearchRunNotFoundError, EvidenceArtifact, LocalSearchFilters (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.19
Nodes (17): date, build_display_query(), build_engine_date_params(), build_engine_query(), _date_range(), _domain_from_site_filter(), _link_matches_filetype(), _link_matches_site() (+9 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (38): AppSettings, EvidenceCaptureError, Raised when an evidence artifact cannot be captured or persisted., InvestigationService, _archive_page(), _archive_page_for_selection_source(), _artifact_file_path(), _cached_history_payload() (+30 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (9): DuckDuckGoSearchEngine, _html_to_visible_text(), looks_like_duckduckgo_forbidden(), looks_like_duckduckgo_robot_challenge(), RobotChallengeError, _create_duckduckgo_engine(), DuckDuckGoParsingTestCase, DuckDuckGoRobotChallengeErrorTestCase (+1 more)

### Community 19 - "Community 19"
Cohesion: 0.19
Nodes (22): applyLanguage(), applySettings(), applyThemeSetting(), broadcastSettings(), currentLanguage(), detectedLanguage(), init(), installDialogTranslations() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (20): apply_cli_runtime_overrides(), _apply_settings_to_tabs(), configure_event_loop_policy(), configure_logging(), _consume_settings_change(), _default_archive_name(), _default_capture_name(), _extension_overlay_context_payload() (+12 more)

### Community 23 - "Community 23"
Cohesion: 0.08
Nodes (10): BraveSearchEngine, Save the raw page once when Brave yields zero results, so its         current m, Construct the query for the search., Wait for Brave's client-rendered results, then read — same strategy         as, _create_brave_engine(), EngineGoldenParsingTestCase, BraveParsingTestCase, ProbePageStateTestCase (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (8): get_browser_service(), Shared :class:`BrowserService` for ``browser`` (one per instance).      Browsers, wait_for_home_action(), ActiveEngineTabSkipTestCase, T-011: the poll loop must not touch tabs owned by a running engine., PushTransportTestCase, T-021: push transport for local pages (home, investigation/report tabs).  `wait_, _ready_state()

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (4): generate_investigation_page(), Path, InvestigationViewTestCase, workspace_payload()

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (7): BraveEmptyResultsDumpTestCase, BraveResultsWaitTestCase, GoogleRobotCheckTestCase, _GoogleRobotTab, A silently empty Brave (both embedded-JSON and XPath parsing miss)     saves the, Brave renders results client-side after a reveal; the wait must hold     for the, T-004: captcha detection uses query_selector and the /sorry/ URL,     and an unr

### Community 28 - "Community 28"
Cohesion: 0.12
Nodes (15): BrowserService, _arm_overlay_focus_guard(), _install_and_consume_save_overlay(), _mark_local_tab_synced(), _overlay_bundle_script(), _overlay_focus_guard_script(), _overlay_injection_blocked(), Whether the per-tick consume/sync evaluate should run for a local     page ``ta (+7 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (5): GraphEntity, HTMLElementTagNameMap, PROPERTY_TYPE_LABELS, HTMLElementTagNameMap, SxOverlaySelectionTrigger

### Community 30 - "Community 30"
Cohesion: 0.06
Nodes (33): SxOverlayRoot, activeContext, applyActionAttributes(), applyButtonStatus(), applyLocalAck(), CaptureAttach, CaptureMenuElement, createActionButton() (+25 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (15): compilerOptions, experimentalDecorators, isolatedModules, lib, module, moduleResolution, noEmit, noUnusedLocals (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (14): dependencies, lit, description, devDependencies, esbuild, typescript, name, private (+6 more)

### Community 35 - "Community 35"
Cohesion: 0.11
Nodes (32): Browser, eval_js(), Evaluate ``script`` on ``tab``, best-effort.      Counts one instrumented call u, _consume_home_tab_action(), _consume_page_tab_action(), _extension_overlay_message(), _extension_overlay_tab_id(), _focus_or_open_home_tab() (+24 more)

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (3): HTMLElementTagNameMap, OverlayActionState, SxOverlayAction

### Community 38 - "Community 38"
Cohesion: 0.10
Nodes (14): ABC, Base exception for application-level Synthesix failures., RobotChallengeError, SearchEngineError, SynthesixError, maybe_log_snapshot(), Process-wide counters for CDP traffic (T-006).  Categories used across the codeb, Log a rate summary at DEBUG level, at most once per ``interval``. (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (8): CATEGORY_COLORS, FALLBACK_PALETTE, GraphData, GraphEdge, GraphNode, HTMLElementTagNameMap, Link, Particle

### Community 40 - "Community 40"
Cohesion: 0.14
Nodes (7): CallJournal, CallRecord, _FakeCookies, _ModuleProxy, Fake Zendriver browser/tab harness shared by Synthesix tests (T-050).  Reference, Pass-through module wrapper overriding a handful of attributes., Timestamped log of every fake call, shared browser <-> tabs.

### Community 41 - "Community 41"
Cohesion: 0.21
Nodes (6): _dictionary_keys(), I18nCoverageTestCase, _numeric_patterns(), Guard tests keeping the cockpit redesign fully internationalized.  Generated p, Every visible home string (and translatable attribute) must resolve         to, multilingual (fr/es/zh) and additionalTranslations (pt/de) must hold         th

### Community 42 - "Community 42"
Cohesion: 0.17
Nodes (8): Window, CaptureAttach, CaptureScope, GraphEntity, HTMLElementTagNameMap, DragState, HTMLElementTagNameMap, OverlayActionElement

### Community 44 - "Community 44"
Cohesion: 0.50
Nodes (4): _detection_title(), _entity_source_heading(), Plain-text detection summary for the info tooltip (native title)., _source_field_label()

### Community 45 - "Community 45"
Cohesion: 0.19
Nodes (13): activeContext, bridgeToken, hasOverlayHost(), injectOverlayScript(), isBlockedOverlayUrl(), observer, postButtonStatus(), postContextUpdate() (+5 more)

### Community 46 - "Community 46"
Cohesion: 0.17
Nodes (5): DataFrame, Exception, _preferred_robot_challenge_artifact(), _robot_challenge_errors(), Semaphore

### Community 48 - "Community 48"
Cohesion: 0.21
Nodes (13): BackendButtonStatusMessage, BackendContextMessage, BackendMessage, canDispatchToBackend(), dispatchToBackend(), isRecord(), normalizeBackendMessage(), queuedMessages (+5 more)

### Community 49 - "Community 49"
Cohesion: 0.14
Nodes (5): GoogleSearchEngine, Best-effort: click the reCAPTCHA "I'm not a robot" checkbox with a         trust, _create_google_engine(), SearchFilters, EngineUrlTestCase

### Community 51 - "Community 51"
Cohesion: 0.25
Nodes (6): assets, common, configs, extensionDist, root, watch

### Community 53 - "Community 53"
Cohesion: 0.14
Nodes (14): Connection, ExtractedEntity, InvestigationEntity, InvestigationResult, ExtractedEntity, InvestigationEntity, InvestigationResult, InvestigationRepository (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.25
Nodes (4): SearchOrchestrator, FakeEngine, ReportCapture, SearchOrchestratorTestCase

### Community 57 - "Community 57"
Cohesion: 0.57
Nodes (3): InvestigationSearchRun, InvestigationSearchRun, Row

### Community 58 - "Community 58"
Cohesion: 0.15
Nodes (12): background, service_worker, type, content_scripts, description, key, manifest_version, minimum_chrome_version (+4 more)

### Community 60 - "Community 60"
Cohesion: 0.23
Nodes (5): BrowserSessionError, ConcurrencyTrackingEngine, QueryAwareEngine, SequenceEngine, SlowEngine

### Community 61 - "Community 61"
Cohesion: 0.17
Nodes (6): HTMLElementTagNameMap, SxChip, HTMLElementTagNameMap, SxExtractedEntityRow, GroupingRule, HTMLElementTagNameMap

### Community 62 - "Community 62"
Cohesion: 0.15
Nodes (12): SynthesixChromeApi, SynthesixChromeInstalledDetails, SynthesixChromeManifest, SynthesixChromeMessageSender, SynthesixChromeRuntime, SynthesixChromeSendResponse, SynthesixChromeStorage, SynthesixChromeStorageArea (+4 more)

### Community 64 - "Community 64"
Cohesion: 0.25
Nodes (11): _capture_open_href(), _compact_url(), _imported_artifact_view(), _inspector_panel(), Compact summary of a saved page, shown in the workspace rail on click., Href to open a capture: the local file for imports (no text-fragment     highli, Resolve a local, openable href for an imported file capture.      Returns ``{", _result_cards() (+3 more)

### Community 66 - "Community 66"
Cohesion: 0.09
Nodes (17): BingSearchEngine, Resolve a Bing ``/ck/a`` redirect to the real destination URL.      Bing wraps, resolve_bing_redirect(), _challenge_excerpt(), _html_to_visible_text(), looks_like_brave_challenge_url(), looks_like_brave_robot_challenge(), _normalize_challenge_text() (+9 more)

### Community 69 - "Community 69"
Cohesion: 0.15
Nodes (13): Single entry point for Zendriver/CDP access (T-020)., click_at(), _InspectorWorkerScriptLoaded, mhtml(), outer_html(), Thin single layer over Zendriver/CDP (T-020).  Every CDP exchange initiated by t, Return the full MHTML snapshot of the page. Exceptions propagate., Return the document outer HTML (no shadow DOM). Exceptions propagate. (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.42
Nodes (4): EvidenceCapture, EvidenceCapture, _capture_datetime(), _has_archive_artifact()

### Community 73 - "Community 73"
Cohesion: 0.20
Nodes (3): Expose ``window.<name>(payload)`` on ``tab`` and route each call         into :a, Expose the dispatch binding on Synthesix' MV3 service worker.          The worke, Deliver a backend-originated message to Synthesix' service worker.          T-03

### Community 75 - "Community 75"
Cohesion: 0.12
Nodes (7): SearchEngine, FlakyParsePooledEngine, HangingTabEngine, PooledStubEngine, First variant fails at parse time, later variants succeed., Real SearchEngine subclass that opens a tab then hangs forever.      Exercises t, Real SearchEngine subclass exercising the T-014 tab pool end to end.

### Community 76 - "Community 76"
Cohesion: 0.35
Nodes (6): _build_country_index(), build_engine_region_params(), CountryRegion, _normalize_country_name(), resolve_country(), SearchRegionsTestCase

### Community 77 - "Community 77"
Cohesion: 0.11
Nodes (10): _log_search_task_outcome(), Run a search concurrently with the action loop (T-011).      The done callback, Background home search; owns the final home statuses., _run_search_action(), _search_task_running(), SearchBrowserProvider, _start_search_task(), Task (+2 more)

### Community 82 - "Community 82"
Cohesion: 0.29
Nodes (3): EngineTabPool, One reusable tab per engine for a whole search run (T-014).      Query variants, Tab

### Community 83 - "Community 83"
Cohesion: 0.13
Nodes (6): FakeBrowser, Scriptable stand-in for ``zendriver.Browser`` (see module docstring)., CdpBudgetTestCase, make_tab(), FakeTab answering the home/overlay/page poll scripts (T-050 harness)., FakeTabBehaviourTestCase

### Community 84 - "Community 84"
Cohesion: 0.27
Nodes (6): _prepare_base_query(), normalize_query_variants(), suggest_query_variants(), _without_accents(), QueryVariantsTestCase, is_advanced_query()

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (4): Page-target ids from zendriver's event-maintained registry., Cheap per-tick liveness signal (no CDP round-trip).          The event-maintaine, Authoritative `getTargets` round-trip: refresh the registry and         report t, Live page tabs, or ``None`` when the browser is unreachable.          Reads zend

### Community 88 - "Community 88"
Cohesion: 0.38
Nodes (6): _asset_prefix(), _filter_summary(), generate_local_search_page(), _relative_href(), _result_card(), LocalSearchViewTestCase

### Community 89 - "Community 89"
Cohesion: 0.40
Nodes (4): Brand, BRANDS, FAVICON_COLORS, HTMLElementTagNameMap

### Community 95 - "Community 95"
Cohesion: 0.50
Nodes (3): looks_like_duckduckgo_no_results(), True when DuckDuckGo explicitly reports an empty result set.      Used to stop w, DuckDuckGoNoResultsTestCase

## Knowledge Gaps
- **122 isolated node(s):** `manifest_version`, `name`, `version`, `description`, `key` (+117 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 8` to `Community 1`, `Community 66`, `Community 35`, `Community 4`, `Community 38`, `Community 7`, `Community 17`, `Community 18`, `Community 83`, `Community 22`, `Community 23`, `Community 24`, `Community 25`, `Community 56`, `Community 60`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `InvestigationService` connect `Community 2` to `Community 96`, `Community 32`, `Community 35`, `Community 5`, `Community 70`, `Community 71`, `Community 6`, `Community 12`, `Community 15`, `Community 80`, `Community 17`, `Community 53`, `Community 22`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `InvestigationRepository` connect `Community 53` to `Community 96`, `Community 32`, `Community 2`, `Community 35`, `Community 5`, `Community 70`, `Community 71`, `Community 15`, `Community 80`, `Community 17`, `Community 57`, `Community 25`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Path` (e.g. with `.test_dumps_even_when_page_mentions_robot()` and `.test_dumps_only_once_per_search()`) actually correct?**
  _`Path` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `InvestigationRepository` (e.g. with `InvestigationHasDataError` and `InvestigationNotFoundError`) actually correct?**
  _`InvestigationRepository` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `InvestigationService` (e.g. with `InvestigationValidationError` and `EvidenceCapture`) actually correct?**
  _`InvestigationService` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `BrowserService` (e.g. with `.test_arm_dispatch_binding_failure_leaves_target_unarmed()` and `.test_arm_dispatch_binding_is_idempotent_per_target()`) actually correct?**
  _`BrowserService` has 22 INFERRED edges - model-reasoned connections that need verification._