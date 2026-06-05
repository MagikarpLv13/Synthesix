# Synthesix

Synthesix is a multi-engine search tool powered by zendriver that allows you to perform precise and advanced queries across several search engines (Google, Bing, Brave, DuckDuckGo). It then synthesizes the results, removes duplicates, and attributes a relevance score to each result based on meta tags and the URL. The top results are presented in a clear, aggregated report.

## Prerequisites

- **Chrome Browser:** The application requires Google Chrome to be installed on your system as it uses Chrome's automation capabilities for search operations.

## Features

- **Multi-engine search:** Query Google, Bing, Brave, and DuckDuckGo simultaneously.
- **Smart query parsing:** Supports both simple and advanced queries, with automatic parsing for improved relevance.
- **Result synthesis:** Merges and deduplicates results from all engines.
- **Relevance scoring:** Each result is scored based on the presence of search terms in the title, description (meta tags), and URL.
- **HTML report generation:** Synthesized results are presented in a user-friendly HTML report.
- **Browser-based interface:** Enter your search directly in the browser UI, no console required.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Synthesix
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **(Optional) Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Usage

1. **Start the application:**
   ```bash
   python main.py
   ```
2. **Interact via the browser:**
   - The browser will open to a simple interface.
   - Enter your search query in the input field and click **Search**.
   - The results will be synthesized and shown in a generated HTML report.
   - Closing all Synthesix tabs exits the application.

## How It Works

- **Query Parsing:**
  - If your query is not in advanced format, Synthesix will parse and optimize it for better results.
- **Parallel Search:**
  - The query is sent in parallel to Google, Bing, Brave, and DuckDuckGo using browser automation.
- **DuckDuckGo no-AI mode:**
  - DuckDuckGo uses the `noai.duckduckgo.com` HTML endpoint with URL parameters that disable Instant Answers, auto-suggest, ads, and Safe Search.
- **Result Aggregation:**
  - Results from all engines are merged and deduplicated by URL.
- **Relevance Scoring:**
  - Each result is scored using a custom algorithm that checks for the presence of search terms in the title, meta description, and URL. Higher scores are given for exact matches and for terms found in more important fields (e.g., title > description > URL).
- **Report Generation:**
  - The top results (by score) are displayed in a synthesized HTML report, including title, description, link, source, and relevance score.

## Advanced Queries

- Synthesix supports advanced queries using logical operators (AND, OR) and quoted phrases.
- Example: `"machine learning" AND Python OR "deep learning"`

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies (includes browser automation and pandas).
- Google Chrome or Chromium available locally for Zendriver/CDP automation.

## Development Checks

Run the local non-browser regression tests:

```bash
python -m unittest discover
```

For a live smoke test, start the app with Chrome/Chromium installed:

```bash
python main.py
```

## Runtime Data

Synthesix writes browser profile data to `zendriver-profile/` and generated reports/history to `history/`. These paths are ignored by Git and should not contain application secrets.

## Configuration

Runtime settings can be overridden with environment variables:

- `SYNTHESIX_BASE_DIR`
- `SYNTHESIX_HISTORY_DIR`
- `SYNTHESIX_HISTORY_REPORT_PATH`
- `SYNTHESIX_BROWSER_PROFILE_DIR`
- `SYNTHESIX_DEFAULT_ENGINES` such as `google,duckduckgo`
- `SYNTHESIX_DEFAULT_MAX_RESULTS`
- `SYNTHESIX_HISTORY_LIMIT`
- `SYNTHESIX_HOME_POLL_INTERVAL`
- `SYNTHESIX_EMPTY_TABS_GRACE_SECONDS`
- `SYNTHESIX_PAGE_LOAD_TIMEOUT`
- `SYNTHESIX_PAGE_LOAD_INTERVAL`
- `SYNTHESIX_BRAVE_RESULTS_TIMEOUT`
- `SYNTHESIX_BRAVE_RESULTS_INTERVAL`
- `SYNTHESIX_BRAVE_ROBOT_FIND_TIMEOUT`
- `SYNTHESIX_ENGINE_SEARCH_TIMEOUT`
- `SYNTHESIX_ENGINE_RETRY_ATTEMPTS`
- `SYNTHESIX_ENGINE_RETRY_DELAY`
- `SYNTHESIX_ENGINE_RETRY_BACKOFF`

---

**Synthesix** — Aggregate, score, and synthesize your search results for maximum relevance.
