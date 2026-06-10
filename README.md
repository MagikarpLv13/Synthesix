# Synthesix

Synthesix is a multi-engine search tool powered by Zendriver and Chrome DevTools Protocol. It runs precise searches across Google, Bing, Brave, and DuckDuckGo, merges duplicated URLs, scores the results, and writes an HTML report with the aggregated output.

The application is async-first and browser-driven: Zendriver controls Chrome/Chromium, while the user interacts with a local browser home page.

## Brand

Synthesix uses the following application palette:

| Role | Color |
| --- | --- |
| Primary blue | `#2563EB` |
| Primary navy | `#0F172A` |
| Secondary cyan | `#06B6D4` |
| Secondary slate | `#64748B` |
| Monochrome black | `#000000` |
| Monochrome white | `#FFFFFF` |

Brand assets live in `assets/`:

| Asset | Purpose |
| --- | --- |
| `synthesix-logo.svg` | Full logo for light backgrounds. |
| `synthesix-logo-dark.svg` | Full logo for dark backgrounds. |
| `synthesix-mark.svg` | Color symbol used in application headers. |
| `synthesix-app-icon.svg` | Square application icon. |
| `favicon.svg` | Browser tab and bookmark favicon. |
| `synthesix-mark-black.svg` | Pure-black monochrome mark. |
| `synthesix-mark-white.svg` | Pure-white monochrome mark. |

The shared `theme.css` applies the palette to the home page, generated history page,
and generated result reports in both light and dark modes.

## Prerequisites

- Python 3.10+.
- Google Chrome or Chromium installed locally.
- Network access to the enabled search engines.
- A writable project directory for runtime files.

Zendriver launches and controls Chrome/Chromium through CDP. If Synthesix is later deployed in Docker or on a server, the image must include Chrome/Chromium and the OS libraries required by headless Chromium.

## Installation

Create and activate a virtual environment first:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` currently pins Zendriver with:

```text
zendriver==0.15.3
```

Keep Zendriver pinned unless you are intentionally testing a browser/CDP compatibility update.

## Usage

Start the application:

```powershell
python main.py
```

Optional logging flags:

```powershell
python main.py --quiet
python main.py --verbose
python main.py --debug-html
```

`--debug-html` keeps unique raw search-engine pages in `history/debug_pages/`. Filenames include the timestamp, engine, and capture stage, for example `20260608_190000_000000_duckduckgo_results.html`. Combine it with `--verbose` to see every saved path in the console:

```powershell
python main.py --debug-html --verbose
```

Synthesix opens a Chrome/Chromium window on the local home page. Enter a query and click **Search**. Results are written to `history/` and opened in browser tabs.

Session behavior:

- Closing all Synthesix tabs stops the program.
- Closing only the original home tab does not stop the program if other Synthesix tabs are still open.
- Searches can optionally be attached to a local investigation from the home page.
- Investigation folders can be created, edited, archived, and deleted while they are empty.
- The generated history page can reopen previous searches.
- The home page includes a default bookmark/favorite entry for returning to Synthesix.
- **Clear Synthesix history** removes saved searches and generated result reports.
- **Clear browser data** restarts the automated browser after removing browsing history, cookies, cache, sessions, and site storage from the Synthesix profile.
- The VPN indicator checks the public IP used by Chrome when the home page opens. Click the indicator to refresh it.

Browser-data cleanup affects only `zendriver-profile/`, not the user's normal Chrome or Brave profile. Synthesix preserves its bookmark and saved browser passwords, but clearing cookies signs out active website sessions.

### Investigation workflow

The investigation selector on the home page is optional. Select **No investigation**
to keep the original standalone search behavior.

For a tracked investigation:

1. Create or select an investigation on the home page.
2. Run searches normally. Search parameters, engine errors, reports, and result
   observations are persisted for provenance, but results are not added to the
   investigation workspace automatically.
3. Open an external HTTP(S) page. Synthesix injects a floating button with its
   mark in the lower-right corner through CDP. It reads **Save page** when a
   case is active, **Saved** when the current page is already retained, or
   **Select investigation** otherwise.
4. Click the button only for pages that should be retained in the investigation.
5. Use the adjacent camera button to capture either the visible viewport or a
   rectangular area selected directly on the page.
6. Click **Open** on the home page to review saved pages with analyst statuses,
   favorites, notes, and tags.
7. Open or delete captures directly from the saved page.
8. Filter saved pages by text, status, source, tag, observation date, or favorite.
9. Attach an earlier unassigned search when its query and observations belong to
   the investigation.

The analyst statuses are `To verify`, `Relevant`, `Discarded`, and `Confirmed`.
They describe the analyst's review state, not the factual reliability of a source.

For each explicitly saved page, Synthesix records:

- the current URL, page title, and meta description;
- the save time and available referring URL;
- the originating query, report, and search engines when the URL matches a
  result observed in the active investigation;
- analyst notes, tags, status, and favorite state.

The floating button is not injected into Synthesix pages or non-HTTP(S) browser
pages. It does not read cookies, authentication data, form values, or page body
content. Without an active investigation, clicking it returns to the Synthesix
home so the analyst can select one.

Reopening a page already saved in the active investigation updates its
**Last seen** timestamp automatically. Investigation pages display stored UTC
timestamps in the browser's local time zone.

PNG evidence captures are explicit and local. The name defaults to
`screenshot_YYYY-MM-DD_HH-MM-SS` in the browser's local time and can be replaced
before capture. The investigation page shows a thumbnail; both the thumbnail and
the capture name open the PNG. For each capture, Synthesix stores the selected
CSS-pixel coordinates, source URL, UTC capture time, browser context, PNG byte
size, SHA-256 hash, and a versioned JSON manifest. The technical manifest and
hash remain in the evidence files without cluttering the investigation page. A
saved page with evidence cannot be removed until its captures are deleted.
The **Verify** action recalculates the PNG SHA-256 locally and reports whether it
still matches the value recorded at capture time. HTML/MHTML capture remains
planned follow-up work.

Archived investigations remain available from the selector and open in read-only
mode. They cannot receive new searches or analyst edits.

### VPN indicator

The home page displays a connection indicator:

- Green, `VPN likely`: the public IP is listed as a known VPN exit node.
- Red, `VPN not detected`: the public IP is not listed as a known VPN exit node.
- Gray/amber, `VPN unknown`: the check is running, unavailable, or timed out.

The check runs from the Chrome page, so it observes the same public route as browser
searches, including browser-level VPNs or proxies when they affect that page. It uses
the anonymous `https://api.ipapi.is` endpoint and therefore sends the browser's public
IP address to that external service. No search query, history entry, cookie, or account
data is sent.

VPN detection is probabilistic. A green indicator means the exit IP is known to the
provider; a red indicator does not prove that no VPN is active. New, private,
residential, corporate, or self-hosted VPN exits can remain undetected.

## Search Behavior

Simple queries are intentionally protected as exact phrases. For example:

```text
recette de pesto
```

is searched as:

```text
"recette de pesto"
```

Advanced queries with explicit operators and quoted phrases are preserved by the parser.

## OSINT Filters

The home page includes an **OSINT filters** panel for common search operators without requiring users to remember engine syntax.

| Field | Intent | Engine query behavior |
| --- | --- | --- |
| Site | Restrict results to one or more domains. | Uses `site:`. |
| Exclude | Remove results containing one or more terms. | Uses `-term` or `-"quoted phrase"`. |
| Title | Require text in the result title. | Uses `intitle:`. |
| URL | Require text in the result URL. | Uses `inurl:` on Google/DuckDuckGo; falls back to a plain term on Bing/Brave. |
| Page text | Bias the engine toward text in the page body. | Uses `intext:` on Google, `inbody:` on Bing/Brave, and a plain term on DuckDuckGo. |
| File | Restrict by file extension. | Uses `filetype:`. |
| Country | Prioritize results for a selected country or market. | Uses each engine's native regional parameter without changing the query text. |
| After | Keep results from or after a selected date. | Uses each compatible engine's native date-range format. |
| Before | Keep results up to a selected date. | Uses each compatible engine's native date-range format. |

Multiple values can be separated with commas in a filter field. Values containing spaces are quoted automatically.

`After` and `Before` use native date pickers and store dates as `YYYY-MM-DD`. Synthesix converts the selected range per engine:

| Engine | Date range sent by Synthesix |
| --- | --- |
| Google | `tbs=cdr:1,cd_min:MM/DD/YYYY,cd_max:MM/DD/YYYY` |
| Brave | `tf=YYYY-MM-DDtoYYYY-MM-DD` |
| DuckDuckGo | `df=YYYY-MM-DD..YYYY-MM-DD` |
| Bing | No custom date range is sent because Bing's public Web search documentation does not define a stable equivalent. |

When only `After` is selected, Brave and DuckDuckGo use the current date as the upper bound. When only `Before` is selected, they use `1970-01-01` as the technical lower bound. Google supports either bound independently.

Synthesix also applies local post-filtering when the condition can be verified from the collected result metadata:

- `site` is checked against the result domain.
- `exclude` is checked against the result title, description, and URL.
- `title` is checked against the result title.
- `url` and `file` are checked against the result URL.
- `page text` is sent to the search engines but is not hard-filtered locally, because result snippets are not reliable full-page text.

Filter-only searches are allowed. For example, leaving the main search box empty and setting `Site = example.com` plus `File = pdf` searches for documents on that domain.

### Country targeting

The `Country` field provides a searchable country list and also accepts direct two-letter
country codes. Common English, French, and local aliases are normalized, so `Sweden`,
`Suede` (with or without accents), `Sverige`, and `SE` all select Sweden.

Synthesix sends the corresponding native regional parameter:

| Engine | Sweden example |
| --- | --- |
| Google | `gl=se` |
| Bing | `cc=SE` |
| Brave | `country=se` |
| DuckDuckGo | `kl=se-sv` |

Country targeting prioritizes the selected market; it is not a strict country-domain
filter. Combine it with `Site = .se` or a specific Swedish domain when the investigation
requires a hard domain restriction. DuckDuckGo targeting is available for the regions
defined by its public settings; unsupported two-letter codes still work on the other
engines and leave DuckDuckGo on its worldwide region.

## Search Engines

| Engine | Status | Notes |
| --- | --- | --- |
| Google | Available | Result parsing depends on Google's current HTML structure. |
| Bing | Available | Result parsing depends on Bing's current HTML structure. |
| Brave | Available | Anti-robot challenges are detected and captured in `history/robot_challenges/` for debugging/resolution. |
| DuckDuckGo | Available | Uses the main Web search for a fuller result set, parses only organic Web results, and loads additional result pages when requested. The HTML endpoint remains a fallback. |

Search engines can change their markup or anti-bot behavior at any time. When a parser starts returning poor results, update only the affected engine and add or adjust a focused test.

## Runtime Data

Synthesix generates local runtime artifacts. They are ignored by Git and should not be committed.

| Path | Role |
| --- | --- |
| `data/synthesix.db` | Versioned SQLite database for investigations, search runs, result observations, and analyst metadata. |
| `data/investigation_pages/` | Regenerated local investigation workspaces. SQLite remains the source of truth. |
| `data/evidence/` | Explicit PNG evidence captures and versioned provenance manifests, grouped by investigation and capture ID. |
| `zendriver-profile/` | Persistent Chrome/Chromium profile used by Zendriver. |
| `history/` | Generated result reports and history page. |
| `history/history.html` | Search history UI. |
| `history/search_results_*.html` | Generated search result reports. |
| `history/robot_challenges/` | Captured Brave and DuckDuckGo anti-robot pages (`.html`, visible `.txt`, and `.png` when available). |
| `history/debug_pages/` | Raw engine HTML pages kept only when debug HTML mode is enabled. |
| `history.html` | Legacy ignored history path. |
| `test_*.html` | Temporary diagnostic captures. |

Do not hardcode credentials or investigation data in source files. If accounts are later configured for OSINT workflows, keep profile data and secrets outside Git.

The existing `history/history.json` file is imported into SQLite once on first launch.
Generated HTML reports remain available for compatibility. Clearing Synthesix history
removes search runs and generated reports but preserves investigation folders and
explicitly saved pages. Their denormalized discovery summary remains readable even
after the original search history has been cleared.

## Configuration

Runtime settings can be overridden with environment variables:

| Variable | Purpose |
| --- | --- |
| `SYNTHESIX_BASE_DIR` | Base directory for runtime path resolution. |
| `SYNTHESIX_DATABASE_PATH` | SQLite database path for investigations and normalized search history. |
| `SYNTHESIX_INVESTIGATION_PAGES_DIR` | Directory for generated local investigation workspaces. |
| `SYNTHESIX_EVIDENCE_DIR` | Directory for PNG evidence artifacts and JSON manifests. |
| `SYNTHESIX_HISTORY_DIR` | Directory for generated reports/history. |
| `SYNTHESIX_HISTORY_REPORT_PATH` | Explicit path for the history HTML page. |
| `SYNTHESIX_DEBUG_HTML` | Enable raw HTML capture with `1`, `true`, `yes`, or `on`. |
| `SYNTHESIX_DEBUG_HTML_DIR` | Directory used for raw engine HTML captures. |
| `SYNTHESIX_BROWSER_PROFILE_DIR` | Chrome/Chromium profile directory. |
| `SYNTHESIX_BROWSER` | Zendriver browser type: `auto`, `chrome`, or `brave`. |
| `SYNTHESIX_BROWSER_EXECUTABLE_PATH` | Explicit Chrome/Brave executable path when autodetection is not enough. |
| `SYNTHESIX_BROWSER_CONNECTION_TIMEOUT` | Delay between Zendriver browser connection checks. |
| `SYNTHESIX_BROWSER_CONNECTION_MAX_TRIES` | Maximum Zendriver browser connection attempts. |
| `SYNTHESIX_DEFAULT_ENGINES` | Comma-separated default engines, such as `google,duckduckgo`. |
| `SYNTHESIX_DEFAULT_MAX_RESULTS` | Default maximum results kept in reports. |
| `SYNTHESIX_HISTORY_LIMIT` | Maximum saved history entries. |
| `SYNTHESIX_HOME_POLL_INTERVAL` | Delay between home/action polling checks. |
| `SYNTHESIX_EMPTY_TABS_GRACE_SECONDS` | Grace period before stopping when no Synthesix tab remains. |
| `SYNTHESIX_PAGE_LOAD_TIMEOUT` | Per-page load timeout. |
| `SYNTHESIX_PAGE_LOAD_INTERVAL` | Polling interval while waiting for a page load. |
| `SYNTHESIX_BRAVE_RESULTS_TIMEOUT` | Brave-specific result wait timeout. |
| `SYNTHESIX_BRAVE_RESULTS_INTERVAL` | Brave-specific result polling interval. |
| `SYNTHESIX_BRAVE_ROBOT_FIND_TIMEOUT` | Brave anti-robot detection timeout. |
| `SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT` | Maximum time allowed for manual DuckDuckGo challenge resolution. |
| `SYNTHESIX_DUCKDUCKGO_ROBOT_INTERVAL` | Polling interval while waiting for DuckDuckGo results after manual resolution. |
| `SYNTHESIX_ENGINE_SEARCH_TIMEOUT` | Global timeout for one engine search. |
| `SYNTHESIX_ENGINE_CONCURRENCY` | Maximum number of engines searched at the same time. |
| `SYNTHESIX_ENGINE_RETRY_ATTEMPTS` | Retry attempts for transient engine failures. |
| `SYNTHESIX_ENGINE_RETRY_DELAY` | Initial retry delay. |
| `SYNTHESIX_ENGINE_RETRY_BACKOFF` | Retry delay multiplier. |

Example:

```powershell
$env:SYNTHESIX_DEFAULT_ENGINES = "google,bing,duckduckgo"
$env:SYNTHESIX_ENGINE_SEARCH_TIMEOUT = "45"
python main.py
```

DuckDuckGo's visual challenge requires manual resolution. Synthesix brings the challenge tab to the foreground, captures it in `history/robot_challenges/`, waits up to 75 seconds by default, and resumes as soon as the normal result container appears. If DuckDuckGo displays an intermediate `Forbidden` page after submission, Synthesix captures it, reloads the original query, then tries the standard HTML endpoint as a fallback. Keep `SYNTHESIX_ENGINE_SEARCH_TIMEOUT` greater than `SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT`.

### Linux Browser Detection

Synthesix resolves the browser executable in this order:

1. `SYNTHESIX_BROWSER_EXECUTABLE_PATH`, when explicitly configured.
2. Chrome/Chromium or Brave commands available on `PATH`.
3. Common Linux and Snap paths such as `/snap/bin/brave`.
4. Brave Flatpak application `com.brave.Browser`.

For Brave Flatpak, Synthesix checks the installation with `flatpak info` and generates an executable launcher in `.cache/synthesix/brave-flatpak`. Zendriver then uses that launcher as its browser executable, so CDP arguments are forwarded to:

```bash
flatpak run com.brave.Browser
```

No user-specific path is hardcoded. A custom launcher remains supported:

```bash
export SYNTHESIX_BROWSER=brave
export SYNTHESIX_BROWSER_EXECUTABLE_PATH="$HOME/bin/brave-flatpak"
python main.py
```

The launcher must be executable and forward every argument received from Zendriver:

```sh
#!/bin/sh
exec flatpak run com.brave.Browser "$@"
```

## Development Checks

Run the non-browser regression tests:

```powershell
venv\Scripts\python.exe -m unittest discover
```

Compile the main modules:

```powershell
venv\Scripts\python.exe -m py_compile main.py utils.py scoring.py google.py bing.py brave.py duckduckgo.py browser_manager.py search_engine.py settings.py search_orchestrator.py exceptions.py parsers.py query_operators.py search_regions.py investigations\__init__.py investigations\models.py investigations\migrations.py investigations\repository.py investigations\service.py investigations\view.py evidence\__init__.py evidence\capture.py evidence\hashing.py evidence\manifest.py
```

Check whitespace before committing:

```powershell
git diff --check
```

Profile Python startup/import overhead:

```powershell
Measure-Command { venv\Scripts\python.exe -c "import main" }
venv\Scripts\python.exe -X importtime -c "import main"
```

Profile the non-browser test suite:

```powershell
Measure-Command { venv\Scripts\python.exe -m unittest discover }
venv\Scripts\python.exe -m cProfile -s cumtime -m unittest discover
```

Optional live smoke test:

```powershell
python main.py
```

Use a small exact query, verify that a report opens, close all Synthesix tabs, then relaunch the app to confirm Chrome does not display an unclean shutdown warning.

## Zendriver Update Procedure

Use this checklist before bumping Zendriver:

1. Update the pinned version in `requirements.txt`.
2. Reinstall dependencies in the virtual environment:

   ```powershell
   venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
   ```

3. Run the local checks:

   ```powershell
   venv\Scripts\python.exe -m py_compile main.py utils.py scoring.py google.py bing.py brave.py duckduckgo.py browser_manager.py search_engine.py settings.py search_orchestrator.py exceptions.py parsers.py query_operators.py search_regions.py investigations\__init__.py investigations\models.py investigations\migrations.py investigations\repository.py investigations\service.py investigations\view.py evidence\__init__.py evidence\capture.py evidence\hashing.py evidence\manifest.py
   venv\Scripts\python.exe -m unittest discover
   git diff --check
   ```

4. Run a live smoke test with Chrome/Chromium:
   - start `python main.py`;
   - launch one exact search;
   - open history and one result report;
   - close the first tab while another Synthesix tab remains;
   - close all tabs and verify the process exits cleanly;
   - relaunch and verify Chrome does not show the unclean shutdown message.

5. If CDP behavior changed, inspect only the affected layer first:
   - `browser_manager.py` for launch/profile/tab lifecycle;
   - `search_engine.py` for navigation and page content retrieval;
   - the affected engine module for parsing or challenge handling.

## Project Layout

| Path | Role |
| --- | --- |
| `main.py` | Browser lifecycle, local UI loop, and report tab opening. |
| `search_orchestrator.py` | Multi-engine orchestration, retries, timeouts, scoring, and report generation. |
| `search_engine.py` | Base engine behavior for navigation, loading, and content retrieval. |
| `query_operators.py` | OSINT filter model, operator rendering, engine-specific query building, and local result filtering. |
| `search_regions.py` | Country-name normalization and engine-specific regional parameters. |
| `investigations/` | Versioned SQLite schema, repositories, domain models, services, and local workspace generation. |
| `evidence/` | Async CDP PNG capture, selection validation, SHA-256 hashing, and versioned provenance manifests. |
| `assets/` | Synthesix logo, app icon, favicon, and monochrome brand marks. |
| `google.py`, `bing.py`, `brave.py`, `duckduckgo.py` | Engine-specific URL construction and parsing. |
| `browser_manager.py` | Zendriver/Chrome profile and tab management helpers. |
| `settings.py` | Runtime configuration and environment variable parsing. |
| `exceptions.py` | Application-level exception types. |
| `utils.py` | HTML report/history generation and query helpers. |
| `scoring.py` | Result scoring logic. |
| `tests/` | Unit tests for settings, scoring, engines, orchestration, errors, and reports. |

## Maintenance Rules

- Keep browser code async; use `await asyncio.sleep()`, not `time.sleep()`.
- Always stop Zendriver/Chrome cleanly through the browser manager or `await browser.stop()`.
- Keep engine failures isolated so one broken engine does not block the others.
- Do not change exact-phrase search behavior without a dedicated test.
- Do not commit generated HTML captures, browser profiles, logs, or secrets.
- Prefer small parser fixes over broad rewrites when search engine markup changes.

---

**Synthesix** - Aggregate, score, and synthesize search results for OSINT-oriented investigation workflows.
