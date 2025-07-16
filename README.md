# Synthesix

Synthesix is a multi-engine search tool powered by zendriver that allows you to perform precise and advanced queries across several search engines (Google, Bing, Brave). It then synthesizes the results, removes duplicates, and attributes a relevance score to each result based on meta tags and the URL. The top results are presented in a clear, aggregated report.

## Prerequisites

- **Chrome Browser:** The application requires Google Chrome to be installed on your system as it uses Chrome's automation capabilities for search operations.

## Features

- **Multi-engine search:** Query Google, Bing, and Brave simultaneously.
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
   - Click **Quit** to exit the application.

## How It Works

- **Query Parsing:**
  - If your query is not in advanced format, Synthesix will parse and optimize it for better results.
- **Parallel Search:**
  - The query is sent in parallel to Google, Bing, and Brave using browser automation.
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

---

**Synthesix** — Aggregate, score, and synthesize your search results for maximum relevance.
