# Graph Report - MSA  (2026-07-06)

## Corpus Check
- 99 files · ~111,119 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1636 nodes · 4205 edges · 84 communities (55 shown, 29 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 261 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3d59dcef`
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

## God Nodes (most connected - your core abstractions)
1. `InvestigationRepository` - 108 edges
2. `InvestigationService` - 98 edges
3. `get_settings()` - 62 edges
4. `generate_investigation_page()` - 62 edges
5. `InvestigationValidationError` - 59 edges
6. `InvestigationRepositoryTestCase` - 57 edges
7. `DuckDuckGoSearchEngine` - 54 edges
8. `SearchFilters` - 54 edges
9. `main()` - 50 edges
10. `SearchOrchestrator` - 48 edges

## Surprising Connections (you probably didn't know these)
- `BingSearchEngine` --uses--> `SearchEngine`  [INFERRED]
  bing.py → search_engine.py
- `BraveSearchEngine` --uses--> `SearchEngine`  [INFERRED]
  brave.py → search_engine.py
- `DuckDuckGoSearchEngine` --uses--> `SearchEngine`  [INFERRED]
  duckduckgo.py → search_engine.py
- `GoogleSearchEngine` --uses--> `SearchEngine`  [INFERRED]
  google.py → search_engine.py
- `SearchEngine` --uses--> `BrowserSessionError`  [INFERRED]
  search_engine.py → exceptions.py

## Import Cycles
- None detected.

## Communities (84 total, 29 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (61): Element, _add_graphml_data(), _append_property(), _best_coordinate_fact(), _build_curated_graph(), build_export_graph(), _capture_has_image(), _content_size() (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (16): Connection, InvestigationNotFoundError, InvestigationResultNotFoundError, ExtractedEntity, InvestigationEntity, InvestigationResult, ExtractedEntity, InvestigationEntity (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (11): InvestigationValidationError, Raised when investigation input does not satisfy application rules., _append_property_value(), _clean_text(), _default_property_key(), _extracted_property_key(), _extracted_property_value(), InvestigationService (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (27): capture_html(), capture_mhtml(), capture_png(), CapturedDocument, CapturedPng, _is_sensitive_field(), normalize_html_text(), normalize_selection() (+19 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (10): BrowserSessionError, Base exception for application-level Synthesix failures., SearchEngineError, SynthesixError, SearchRunResult, DummySearchEngine, FailingBrowser, LoadedTab (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (40): _append_match(), _clean_matched_value(), _date_value(), _digits(), EntityCandidate, extract_entity_candidates(), _extract_from_text(), _inferred_field_label() (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (20): datetime, UtilsTestCase, add_to_history(), _asset_prefix(), _brand_markup(), clear_synthesix_history(), generate_history_html(), generate_html_report() (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (16): _bookmark_folder(), _browser_types_to_try(), _build_zendriver_config(), _chrome_timestamp(), _clear_profile_browsing_data(), _ensure_flatpak_brave_wrapper(), _ensure_synthesix_bookmark(), _find_native_browser_executable() (+8 more)

### Community 9 - "Community 9"
Cohesion: 0.16
Nodes (8): fake_clock(), FakeElement, Fake Zendriver browser/tab harness shared by Synthesix tests (T-050).  Reference, Patch ``time.monotonic`` and ``asyncio.sleep`` inside ``modules``.      Only the, Minimal DOM node double (truthy, clickable)., EngineWaitExampleTestCase, ProbeEngine, T-050: example tests for the shared FakeTab/FakeBrowser harness.  One test per d

### Community 10 - "Community 10"
Cohesion: 0.19
Nodes (4): FakeTab, Scriptable stand-in for ``zendriver.Tab`` (see module docstring)., Fallback handler called with the call's positional arguments., CaptureExampleTestCase

### Community 11 - "Community 11"
Cohesion: 0.18
Nodes (3): DataFrame, Exception, Semaphore

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (12): _challenge_excerpt(), _html_to_visible_text(), looks_like_brave_robot_challenge(), _normalize_challenge_text(), parse_with_xpath(), Parse generic search results from HTML using provided XPaths.     Args:, _build_country_index(), build_engine_region_params() (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (43): _compact_url(), _display_datetime(), _doc_kind_badge(), _dom_id_fragment(), _entity_rows_markup(), _entity_status_options(), _entity_type_options(), _evidence_markup() (+35 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (34): _asset_prefix(), _filter_summary(), generate_local_search_page(), _relative_href(), _result_card(), LocalSearchViewTestCase, chip(), context_bar() (+26 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (9): _consume_home_tab_action(), _consume_page_tab_action(), _is_external_web_tab(), _push_home_tab_data(), Light per-tick probe: consume one queued action and report the data     version, Ship history/investigations payloads to a home tab.      Each part is only emb, wait_for_home_action(), T-006: lock the CDP call budget of the idle poll loop.  Simulates `wait_for_home (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (18): date, build_display_query(), build_engine_date_params(), build_engine_query(), _date_range(), _domain_from_site_filter(), _link_matches_filetype(), _link_matches_site() (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (35): AppSettings, EvidenceCaptureError, Raised when an evidence artifact cannot be captured or persisted., InvestigationService, _archive_page(), _archive_page_for_selection_source(), _artifact_file_path(), _cached_history_payload() (+27 more)

### Community 18 - "Community 18"
Cohesion: 0.10
Nodes (7): DuckDuckGoSearchEngine, _html_to_visible_text(), looks_like_duckduckgo_forbidden(), looks_like_duckduckgo_robot_challenge(), _create_duckduckgo_engine(), DuckDuckGoParsingTestCase, DuckDuckGoRobotChallengeErrorTestCase

### Community 19 - "Community 19"
Cohesion: 0.19
Nodes (22): applyLanguage(), applySettings(), applyThemeSetting(), broadcastSettings(), currentLanguage(), detectedLanguage(), init(), installDialogTranslations() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (19): apply_cli_runtime_overrides(), _apply_settings_to_tabs(), _attach_selection_to_graph_entity(), configure_event_loop_policy(), configure_logging(), _consume_settings_change(), _create_graph_entity_from_selection(), _default_archive_name() (+11 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (6): BraveSearchEngine, Construct the query for the search., _create_brave_engine(), BraveRobotChallengeErrorTestCase, js_like_to_json(), Convert a JS like text to a JSON object      Args:         js_text (str): The

### Community 24 - "Community 24"
Cohesion: 0.13
Nodes (11): _arm_overlay_focus_guard(), _install_and_consume_save_overlay(), _overlay_bundle_script(), _overlay_focus_guard_script(), _overlay_injection_blocked(), JS armed early (before any page script) so it wins the DOM event     ordering r, Register the focus-guard script for future navigations of ``tab``.      Best-e, Skip overlay injection on surfaces where it breaks or crashes Chrome.      Goo (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (4): generate_investigation_page(), Path, InvestigationViewTestCase, workspace_payload()

### Community 27 - "Community 27"
Cohesion: 0.16
Nodes (5): GoogleSearchEngine, _create_google_engine(), GoogleRobotCheckTestCase, _GoogleRobotTab, T-004: captcha detection uses query_selector and the /sorry/ URL,     and an unr

### Community 28 - "Community 28"
Cohesion: 0.11
Nodes (11): BingSearchEngine, Resolve a Bing ``/ck/a`` redirect to the real destination URL.      Bing wraps, resolve_bing_redirect(), looks_like_brave_challenge_url(), looks_like_duckduckgo_no_results(), True when DuckDuckGo explicitly reports an empty result set.      Used to stop w, _create_bing_engine(), BingPaginationTestCase (+3 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (5): GraphEntity, HTMLElementTagNameMap, PROPERTY_TYPE_LABELS, HTMLElementTagNameMap, SxOverlaySelectionTrigger

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (15): compilerOptions, experimentalDecorators, isolatedModules, lib, module, moduleResolution, noEmit, noUnusedLocals (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.12
Nodes (15): InvestigationError, InvestigationHasDataError, Base exception for investigation storage and workflow failures., SearchRunNotFoundError, EvidenceArtifact, LocalSearchFilters, LocalSearchResult, PageComparison (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (14): dependencies, lit, description, devDependencies, esbuild, typescript, name, private (+6 more)

### Community 35 - "Community 35"
Cohesion: 0.22
Nodes (16): Browser, _focus_or_open_home_tab(), _is_home_tab(), _normalize_tab_url(), _open_or_refresh_investigation_page(), _open_tabs(), perform_search(), Toggle the home 'search running' UI state (cancel button). (+8 more)

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (3): HTMLElementTagNameMap, OverlayActionState, SxOverlayAction

### Community 38 - "Community 38"
Cohesion: 0.40
Nodes (4): Brand, BRANDS, FAVICON_COLORS, HTMLElementTagNameMap

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (8): CATEGORY_COLORS, FALLBACK_PALETTE, GraphData, GraphEdge, GraphNode, HTMLElementTagNameMap, Link, Particle

### Community 40 - "Community 40"
Cohesion: 0.21
Nodes (4): CallJournal, CallRecord, _FakeCookies, Timestamped log of every fake call, shared browser <-> tabs.

### Community 41 - "Community 41"
Cohesion: 0.21
Nodes (6): _dictionary_keys(), I18nCoverageTestCase, _numeric_patterns(), Guard tests keeping the cockpit redesign fully internationalized.  Generated p, Every visible home string (and translatable attribute) must resolve         to, multilingual (fr/es/zh) and additionalTranslations (pt/de) must hold         th

### Community 42 - "Community 42"
Cohesion: 0.17
Nodes (8): Window, CaptureAttach, CaptureScope, GraphEntity, HTMLElementTagNameMap, DragState, HTMLElementTagNameMap, OverlayActionElement

### Community 44 - "Community 44"
Cohesion: 0.13
Nodes (18): _default_entity_category(), _default_property_key(), _detection_title(), _entity_markup(), _entity_property_key(), _entity_property_type(), _entity_source_heading(), _extracted_entity_row() (+10 more)

### Community 45 - "Community 45"
Cohesion: 0.27
Nodes (6): _prepare_base_query(), normalize_query_variants(), suggest_query_variants(), _without_accents(), QueryVariantsTestCase, is_advanced_query()

### Community 46 - "Community 46"
Cohesion: 0.20
Nodes (15): _build_settings(), _env_bool(), _env_engines(), _env_float(), _env_int(), _env_optional_path(), _env_path(), _env_signature() (+7 more)

### Community 49 - "Community 49"
Cohesion: 0.12
Nodes (8): HTMLElementTagNameMap, SxChip, HTMLElementTagNameMap, SxEntity, HTMLElementTagNameMap, SxEvidenceItem, GroupingRule, HTMLElementTagNameMap

### Community 51 - "Community 51"
Cohesion: 0.33
Nodes (5): assets, common, configs, root, watch

### Community 53 - "Community 53"
Cohesion: 0.12
Nodes (4): Any, _ModuleProxy, Queue successive responses for ``method`` (FIFO)., Pass-through module wrapper overriding a handful of attributes.

### Community 56 - "Community 56"
Cohesion: 0.18
Nodes (9): RobotChallengeError, SearchOrchestrator, ConcurrencyTrackingEngine, FakeEngine, QueryAwareEngine, ReportCapture, SearchOrchestratorTestCase, SequenceEngine (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.19
Nodes (11): add_context_to_breakdown(), build_relevance_explainer(), build_relevance_scorer(), calculate_relevance(), extract_scoring_terms(), Calcul relevance score      Args:         row (dict): row of the dataframe, ScoreBreakdown, ScoreComponent (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.21
Nodes (4): FakeBrowser, Scriptable stand-in for ``zendriver.Browser`` (see module docstring)., FakeTabBehaviourTestCase, HomeActionExampleTestCase

### Community 62 - "Community 62"
Cohesion: 0.11
Nodes (12): ABC, Execute the search and return the results., Set the selector for the search engine.         Selector used as a reference poi, Construct the URL for the search., Parse the raw HTML and return a list of structured results., Return a dictionary with the XPaths necessary for parsing., Used to execute actions after the first search is executed. Mostly for search en, Used to execute actions before the search is executed. (+4 more)

### Community 64 - "Community 64"
Cohesion: 0.22
Nodes (10): _archive_artifact(), _archive_href(), _capture_open_href(), _graph_entities_markup(), _has_archive_artifact(), _imported_doc_kind(), _protected_capture_ids(), Coarse file-type key (image/pdf/audio/video/document/file) for an     imported (+2 more)

### Community 69 - "Community 69"
Cohesion: 0.25
Nodes (3): maybe_log_snapshot(), Process-wide counters for CDP traffic (T-006).  Categories used across the codeb, Log a rate summary at DEBUG level, at most once per ``interval``.

### Community 73 - "Community 73"
Cohesion: 0.28
Nodes (3): CdpBudgetTestCase, make_tab(), FakeTab answering the home/overlay/page poll scripts (T-050 harness).

### Community 75 - "Community 75"
Cohesion: 0.25
Nodes (3): SearchEngine, HangingTabEngine, Real SearchEngine subclass that opens a tab then hangs forever.      Exercises t

### Community 77 - "Community 77"
Cohesion: 0.18
Nodes (7): _log_search_task_outcome(), Run a search concurrently with the action loop (T-011).      The done callback, _search_task_running(), _start_search_task(), Task, BackgroundSearchTaskTestCase, T-011: searches run as background tasks; the loop stays responsive.

### Community 79 - "Community 79"
Cohesion: 0.42
Nodes (4): EvidenceCapture, EvidenceCapture, _capture_datetime(), _has_archive_artifact()

### Community 81 - "Community 81"
Cohesion: 0.42
Nodes (3): aggregate_search_results(), SearchFilters, AggregateSearchResultsTestCase

### Community 83 - "Community 83"
Cohesion: 0.57
Nodes (3): InvestigationSearchRun, InvestigationSearchRun, Row

## Knowledge Gaps
- **74 isolated node(s):** `Window`, `CaptureScope`, `GraphEntity`, `CaptureAttach`, `HTMLElementTagNameMap` (+69 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 46` to `Community 35`, `Community 4`, `Community 7`, `Community 8`, `Community 11`, `Community 12`, `Community 15`, `Community 17`, `Community 18`, `Community 25`, `Community 22`, `Community 23`, `Community 56`, `Community 57`, `Community 62`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `InvestigationRepository` connect `Community 1` to `Community 32`, `Community 2`, `Community 66`, `Community 5`, `Community 79`, `Community 80`, `Community 17`, `Community 82`, `Community 83`, `Community 25`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `InvestigationService` connect `Community 2` to `Community 32`, `Community 1`, `Community 66`, `Community 35`, `Community 5`, `Community 6`, `Community 79`, `Community 80`, `Community 17`, `Community 82`, `Community 22`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `InvestigationRepository` (e.g. with `InvestigationHasDataError` and `InvestigationNotFoundError`) actually correct?**
  _`InvestigationRepository` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Path` (e.g. with `.test_archived_workspace_disables_analyst_mutations()` and `.test_compacts_long_urls_without_changing_link_target()`) actually correct?**
  _`Path` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `InvestigationService` (e.g. with `InvestigationValidationError` and `EvidenceCapture`) actually correct?**
  _`InvestigationService` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Light per-tick probe: consume one queued action and report the data     version`, `Ship history/investigations payloads to a home tab.      Each part is only emb`, `JS armed early (before any page script) so it wins the DOM event     ordering r` to the rest of the system?**
  _169 weakly-connected nodes found - possible documentation gaps or missing edges._