# Synthesix

Synthesix is a multi-engine search tool powered by Zendriver and Chrome DevTools Protocol. It runs precise searches across Google, Bing, Brave, and DuckDuckGo, merges duplicated URLs, scores the results, and writes an HTML report with the aggregated output.

The application is async-first and browser-driven: Zendriver controls Chrome/Chromium, while the user interacts with a local browser home page.

## Prerequisites

- Python 3.8+.
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

Synthesix opens a Chrome/Chromium window on the local home page. Enter a query and click **Search**. Results are written to `history/` and opened in browser tabs.

Session behavior:

- Closing all Synthesix tabs stops the program.
- Closing only the original home tab does not stop the program if other Synthesix tabs are still open.
- The generated history page can reopen previous searches.
- The home page includes a default bookmark/favorite entry for returning to Synthesix.

## Search Behavior

Simple queries are intentionally protected as exact phrases. For example:

```text
starvos and lynch
```

is searched as:

```text
"starvos and lynch"
```

Advanced queries with explicit operators and quoted phrases are preserved by the parser.

## Search Engines

| Engine | Status | Notes |
| --- | --- | --- |
| Google | Available | Result parsing depends on Google's current HTML structure. |
| Bing | Available | Result parsing depends on Bing's current HTML structure. |
| Brave | Available | Anti-robot challenges are detected and captured in `history/robot_challenges/` for debugging/resolution. |
| DuckDuckGo | Available | Uses the `noai.duckduckgo.com` HTML endpoint with parameters oriented toward pure search, without AI/suggested blocks when DuckDuckGo accepts them. |

Search engines can change their markup or anti-bot behavior at any time. When a parser starts returning poor results, update only the affected engine and add or adjust a focused test.

## Runtime Data

Synthesix generates local runtime artifacts. They are ignored by Git and should not be committed.

| Path | Role |
| --- | --- |
| `zendriver-profile/` | Persistent Chrome/Chromium profile used by Zendriver. |
| `history/` | Generated result reports and history page. |
| `history/history.html` | Search history UI. |
| `history/search_results_*.html` | Generated search result reports. |
| `history/robot_challenges/` | Captured anti-robot pages, especially Brave challenges. |
| `history.html` | Legacy ignored history path. |
| `test_*.html` | Temporary diagnostic captures. |

Do not hardcode credentials or investigation data in source files. If accounts are later configured for OSINT workflows, keep profile data and secrets outside Git.

## Configuration

Runtime settings can be overridden with environment variables:

| Variable | Purpose |
| --- | --- |
| `SYNTHESIX_BASE_DIR` | Base directory for runtime path resolution. |
| `SYNTHESIX_HISTORY_DIR` | Directory for generated reports/history. |
| `SYNTHESIX_HISTORY_REPORT_PATH` | Explicit path for the history HTML page. |
| `SYNTHESIX_BROWSER_PROFILE_DIR` | Chrome/Chromium profile directory. |
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
| `SYNTHESIX_ENGINE_SEARCH_TIMEOUT` | Global timeout for one engine search. |
| `SYNTHESIX_ENGINE_RETRY_ATTEMPTS` | Retry attempts for transient engine failures. |
| `SYNTHESIX_ENGINE_RETRY_DELAY` | Initial retry delay. |
| `SYNTHESIX_ENGINE_RETRY_BACKOFF` | Retry delay multiplier. |

Example:

```powershell
$env:SYNTHESIX_DEFAULT_ENGINES = "google,bing,duckduckgo"
$env:SYNTHESIX_ENGINE_SEARCH_TIMEOUT = "45"
python main.py
```

## Development Checks

Run the non-browser regression tests:

```powershell
venv\Scripts\python.exe -m unittest discover
```

Compile the main modules:

```powershell
venv\Scripts\python.exe -m py_compile main.py utils.py scoring.py google.py bing.py brave.py duckduckgo.py browser_manager.py search_engine.py settings.py search_orchestrator.py exceptions.py
```

Check whitespace before committing:

```powershell
git diff --check
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
   venv\Scripts\python.exe -m py_compile main.py utils.py scoring.py google.py bing.py brave.py duckduckgo.py browser_manager.py search_engine.py settings.py search_orchestrator.py exceptions.py
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
