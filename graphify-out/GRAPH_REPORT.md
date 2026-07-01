# Graph Report - MSA  (2026-07-01)

## Corpus Check
- 90 files · ~100,476 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1420 nodes · 3721 edges · 60 communities (38 shown, 22 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 229 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d59c2fab`
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
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 67|Community 67]]

## God Nodes (most connected - your core abstractions)
1. `InvestigationRepository` - 105 edges
2. `InvestigationService` - 95 edges
3. `InvestigationValidationError` - 59 edges
4. `generate_investigation_page()` - 57 edges
5. `DuckDuckGoSearchEngine` - 54 edges
6. `SearchFilters` - 54 edges
7. `get_settings()` - 52 edges
8. `InvestigationRepositoryTestCase` - 49 edges
9. `main()` - 45 edges
10. `SearchOrchestrator` - 43 edges

## Surprising Connections (you probably didn't know these)
- `InvestigationRepository` --uses--> `InvestigationHasDataError`  [INFERRED]
  investigations/repository.py → exceptions.py
- `InvestigationRepository` --uses--> `InvestigationValidationError`  [INFERRED]
  investigations/repository.py → exceptions.py
- `InvestigationRepository` --uses--> `SearchRunNotFoundError`  [INFERRED]
  investigations/repository.py → exceptions.py
- `InvestigationRepositoryTestCase` --uses--> `InvestigationRepository`  [INFERRED]
  tests/test_investigations.py → investigations/repository.py
- `InvestigationRepositoryTestCase` --uses--> `InvestigationService`  [INFERRED]
  tests/test_investigations.py → investigations/service.py

## Import Cycles
- None detected.

## Communities (60 total, 22 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (58): Element, _add_graphml_data(), _append_property(), _best_coordinate_fact(), _build_curated_graph(), build_export_graph(), _content_size(), _coordinates() (+50 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (13): Connection, InvestigationNotFoundError, InvestigationResultNotFoundError, ExtractedEntity, InvestigationEntity, InvestigationResult, ExtractedEntity, InvestigationEntity (+5 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (13): InvestigationValidationError, Raised when investigation input does not satisfy application rules., LocalSearchFilters, _append_property_value(), _clean_text(), _default_property_key(), _extracted_property_key(), _extracted_property_value() (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (27): capture_html(), capture_mhtml(), capture_png(), CapturedDocument, CapturedPng, _is_sensitive_field(), normalize_html_text(), normalize_selection() (+19 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (13): InvestigationError, InvestigationHasDataError, Base exception for investigation storage and workflow failures., SearchRunNotFoundError, LocalSearchResult, PageComparison, UrlAnalysis, canonicalize_url() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (40): _append_match(), _clean_matched_value(), _date_value(), _digits(), EntityCandidate, extract_entity_candidates(), _extract_from_text(), _inferred_field_label() (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (19): UtilsTestCase, add_to_history(), _asset_prefix(), _brand_markup(), clear_synthesix_history(), generate_history_html(), generate_html_report(), _history_sort_key() (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (16): _bookmark_folder(), _browser_types_to_try(), _build_zendriver_config(), _chrome_timestamp(), _clear_profile_browsing_data(), _ensure_flatpak_brave_wrapper(), _ensure_synthesix_bookmark(), _find_native_browser_executable() (+8 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (6): Any, EvidenceCapture, EvidenceArtifact, EvidenceCapture, _capture_datetime(), _has_archive_artifact()

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (21): date, datetime, build_display_query(), build_engine_date_params(), build_engine_query(), _date_range(), _domain_from_site_filter(), _link_matches_filetype() (+13 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (16): _html_to_visible_text(), looks_like_duckduckgo_forbidden(), looks_like_duckduckgo_no_results(), looks_like_duckduckgo_robot_challenge(), True when DuckDuckGo explicitly reports an empty result set.      Used to stop w, Custom function to wait for the page to load., Check if we are flagged as a robot., _env_bool() (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.27
Nodes (6): _build_country_index(), build_engine_region_params(), CountryRegion, _normalize_country_name(), resolve_country(), SearchRegionsTestCase

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (80): Declared zeroneurone PropertyType for a canonical tagset key, else ''., zeroneurone_property_type(), _archive_artifact(), _archive_href(), _capture_open_href(), _compact_url(), _default_entity_category(), _default_property_key() (+72 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (34): _asset_prefix(), _filter_summary(), generate_local_search_page(), _relative_href(), _result_card(), LocalSearchViewTestCase, chip(), context_bar() (+26 more)

### Community 15 - "Community 15"
Cohesion: 0.22
Nodes (13): Browser, _consume_home_tab_action(), _consume_page_tab_action(), _focus_or_open_home_tab(), _is_home_tab(), _normalize_tab_url(), _open_or_refresh_investigation_page(), _open_tabs() (+5 more)

### Community 16 - "Community 16"
Cohesion: 0.19
Nodes (11): add_context_to_breakdown(), build_relevance_explainer(), build_relevance_scorer(), calculate_relevance(), extract_scoring_terms(), Calcul relevance score      Args:         row (dict): row of the dataframe, ScoreBreakdown, ScoreComponent (+3 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (34): AppSettings, EvidenceCaptureError, Raised when an evidence artifact cannot be captured or persisted., InvestigationService, _archive_page(), _archive_page_for_selection_source(), _artifact_file_path(), _cached_history_payload() (+26 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (3): DuckDuckGoSearchEngine, DuckDuckGoParsingTestCase, DuckDuckGoRobotChallengeErrorTestCase

### Community 19 - "Community 19"
Cohesion: 0.19
Nodes (22): applyLanguage(), applySettings(), applyThemeSetting(), broadcastSettings(), currentLanguage(), detectedLanguage(), init(), installDialogTranslations() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (17): apply_cli_runtime_overrides(), _apply_settings_to_tabs(), configure_event_loop_policy(), configure_logging(), _consume_settings_change(), _create_graph_entity_from_selection(), _default_archive_name(), _default_capture_name() (+9 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (12): BraveSearchEngine, _challenge_excerpt(), _html_to_visible_text(), looks_like_brave_challenge_url(), looks_like_brave_robot_challenge(), _normalize_challenge_text(), Construct the query for the search., _create_brave_engine() (+4 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (6): _install_and_consume_save_overlay(), _overlay_bundle_script(), _overlay_injection_blocked(), Skip overlay injection on surfaces where it breaks or crashes Chrome.      Goo, OverlayBundleReuseTestCase, OverlayInjectionGuardTestCase

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (3): DataFrame, Exception, Semaphore

### Community 27 - "Community 27"
Cohesion: 0.10
Nodes (13): BingSearchEngine, Resolve a Bing ``/ck/a`` redirect to the real destination URL.      Bing wraps, resolve_bing_redirect(), GoogleSearchEngine, parse_with_xpath(), Parse generic search results from HTML using provided XPaths.     Args:, _create_bing_engine(), _create_duckduckgo_engine() (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.07
Nodes (28): ABC, BrowserSessionError, Base exception for application-level Synthesix failures., RobotChallengeError, SearchEngineError, SynthesixError, Execute the search and return the results., Set the selector for the search engine.         Selector used as a reference po (+20 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (5): GraphEntity, HTMLElementTagNameMap, PROPERTY_TYPE_LABELS, HTMLElementTagNameMap, SxOverlaySelectionTrigger

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (15): compilerOptions, experimentalDecorators, isolatedModules, lib, module, moduleResolution, noEmit, noUnusedLocals (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (4): _attach_selection_to_graph_entity(), _capture_evidence(), _retry_search_combination(), InvestigationPageRoutingTestCase

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (14): dependencies, lit, description, devDependencies, esbuild, typescript, name, private (+6 more)

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (3): HTMLElementTagNameMap, OverlayActionState, SxOverlayAction

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (8): CATEGORY_COLORS, FALLBACK_PALETTE, GraphData, GraphEdge, GraphNode, HTMLElementTagNameMap, Link, Particle

### Community 40 - "Community 40"
Cohesion: 0.27
Nodes (6): _prepare_base_query(), normalize_query_variants(), suggest_query_variants(), _without_accents(), QueryVariantsTestCase, is_advanced_query()

### Community 41 - "Community 41"
Cohesion: 0.21
Nodes (6): _dictionary_keys(), I18nCoverageTestCase, _numeric_patterns(), Guard tests keeping the cockpit redesign fully internationalized.  Generated p, Every visible home string (and translatable attribute) must resolve         to, multilingual (fr/es/zh) and additionalTranslations (pt/de) must hold         th

### Community 42 - "Community 42"
Cohesion: 0.18
Nodes (8): Window, CaptureAttach, CaptureScope, GraphEntity, HTMLElementTagNameMap, DragState, HTMLElementTagNameMap, OverlayActionElement

### Community 46 - "Community 46"
Cohesion: 0.57
Nodes (3): InvestigationSearchRun, InvestigationSearchRun, Row

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (7): HTMLElementTagNameMap, SxChip, HTMLElementTagNameMap, Brand, BRANDS, FAVICON_COLORS, HTMLElementTagNameMap

### Community 51 - "Community 51"
Cohesion: 0.33
Nodes (5): assets, common, configs, root, watch

## Knowledge Gaps
- **68 isolated node(s):** `HTMLElementTagNameMap`, `CaptureScope`, `GraphEntity`, `CaptureAttach`, `HTMLElementTagNameMap` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InvestigationService` connect `Community 2` to `Community 32`, `Community 1`, `Community 35`, `Community 4`, `Community 5`, `Community 9`, `Community 44`, `Community 45`, `Community 15`, `Community 17`, `Community 22`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `InvestigationRepository` connect `Community 1` to `Community 2`, `Community 35`, `Community 4`, `Community 5`, `Community 9`, `Community 44`, `Community 45`, `Community 46`, `Community 13`, `Community 17`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `InvestigationRepositoryTestCase` connect `Community 5` to `Community 1`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `InvestigationRepository` (e.g. with `InvestigationHasDataError` and `InvestigationNotFoundError`) actually correct?**
  _`InvestigationRepository` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `Path` (e.g. with `.test_archived_workspace_disables_analyst_mutations()` and `.test_compacts_long_urls_without_changing_link_target()`) actually correct?**
  _`Path` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `InvestigationService` (e.g. with `InvestigationValidationError` and `EvidenceCapture`) actually correct?**
  _`InvestigationService` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InvestigationValidationError` (e.g. with `InvestigationRepository` and `InvestigationService`) actually correct?**
  _`InvestigationValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._