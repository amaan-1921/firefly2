# Web Scraping Agent Execution Guide

## Setup

```bash
# activate virtual environment
source venv/bin/activate

# navigate to agent_test folder
cd backend/app/services/monitoring/news_intelligence/agent_test

# Install dependencies 
pip install -r ../../../../../../requirements.txt

# Install additional dependencies for RSS parsing
pip install feedparser
```

## Running the Agent

```bash
# Basic run (uses RSS feeds + predefined sources)
python agent.py

# With custom options
python agent.py --num-queries 10 --threshold 0.8 --timewindow 30

# Overwrite output file instead of appending
python agent.py --overwrite

# Custom output file
python agent.py --output my_articles.jsonl
```

## Command Line Options

- `--num-queries N`: Number of search queries to generate (default: 5)
- `--results-per-query N`: Results per query from search engine (default: 10)
- `--timewindow DAYS`: Days to look back for articles (default: 20)
- `--threshold SCORE`: Relevance threshold 0.0-1.0 (default: 0.7)
- `--output FILE`: Output JSONL filename (default: scraped_articles.jsonl)
- `--overwrite`: Overwrite output file instead of appending

## Pipeline Execution

The agent executes 7 main steps:

### Step 1: Generate Search Queries
- Uses LLM (Groq) to generate targeted queries from 63 supply chain topics
- Topics include: disruptions, natural disasters, strikes, shortages, **tariffs, trade wars, geopolitical tensions**

### Step 2: Fetch Article URLs
- **Primary source: RSS feeds** (no rate-limiting)
  - Fetches from: Supply Chain Dive, JOC, Logistics Management, DC Velocity, FreightWaves, Supply Chain Brain
  - ~50 articles per source per run (300+ total)
- Secondary source: Google search (disabled by default, can enable with `USE_GOOGLE_SEARCH=True`)

### Step 3: Scrape Article Content
- Fetches HTML from each URL
- Handles retries with exponential backoff (3 attempts)
- Uses browser-like headers to bypass anti-bot detection
- Rate limiting: 1 second between requests

### Step 4: Extract Metadata
- Extracts: title, publisher, published date, content
- Parses dates from multiple sources (meta tags, HTML content)
- Falls back to scrape timestamp if no date found

### Step 5: Filter by Time Window
- Removes articles older than specified days (default: 20)
- Preserves articles without dates

### Step 6: Score Relevance
- Batches articles (10 per batch)
- Sends to Groq LLM with 97 supply chain keywords
- Keywords now include: **tariff, trade war, embargo, sanction, regulation, geopolitical, conflict**
- Scores 0.0-1.0, filters by threshold (default: 0.7)

### Step 7: Write Output
- Deduplicates against existing file (URL-based)
- Fixed dedup logic: prevents non-duplicates from being filtered
- Appends to `scraped_articles.jsonl` by default
- Logs: articles kept, duplicates filtered, final count

## Key Features & Recent Improvements

### Deduplication Bug Fix
- **Problem**: Articles were incorrectly filtered as duplicates within same batch
- **Fix**: Separate tracking for file-level duplicates vs. batch-level duplicates
- **Result**: No more false positives when appending new articles

### Political/Geopolitical Coverage
- **Added**: 14 new search topics (tariffs, trade wars, sanctions, conflicts)
- **Added**: 8 new relevance keywords (tariff, embargo, geopolitical, etc.)
- **Result**: Captures news about trade restrictions, tariffs, sanctions, international tensions

### RSS Feed Integration
- **Why**: Google search returns 0 results due to rate-limiting
- **Solution**: Use RSS feeds as primary source (designed for automated consumption)
- **Result**: 300+ articles per run with no rate-limiting

### Enhanced Web Scraper
- **Headers**: Now mimics real Chrome browser to bypass 403 Forbidden errors
- **Referer**: Set to Google to appear as referral
- **Security headers**: Includes Sec-Fetch-* headers for authenticity

### Search Engine Fix
- **Problem**: Using wrong API parameters (`num`, `stop`, `pause`)
- **Fix**: Correct parameters (`num_results`, `sleep_interval`)
- **Status**: Google search disabled by default due to rate-limiting

## Output Format

Each article stored in `scraped_articles.jsonl` contains:

```json
{
  "title": "Article title",
  "url": "https://source.com/article",
  "source": "source.com",
  "publisher": "News Organization",
  "published_date": "2026-01-22T12:00:00",
  "content": "Article text...",
  "scraped_at": "2026-01-22T12:05:00",
  "relevance_score": 0.85,
  "relevance_reason": "supply chain disruption"
}
```

## Troubleshooting

**No articles in output?**
- Check relevance threshold (try lowering to 0.5)
- Verify GROQ_API_KEY is set in .env
- Check time window isn't too restrictive

**403 Forbidden errors?**
- Normal for some sites (porttechnology.org blocks scrapers)
- Agent continues with other sources
- Most articles come from RSS feeds (not affected)

**0 articles from Google search?**
- Google rate-limiting is active
- Use RSS feeds instead (USE_GOOGLE_SEARCH=False by default)
- Or get Google Custom Search API credentials

**Duplicates not filtered?**
- Check URL normalization (case, trailing slash)
- Run with `--overwrite` to reset and start fresh

## Configuration

Edit `config.py` to customize:
- `RELEVANCE_THRESHOLD`: 0.7 (default, lower = more articles)
- `TIME_WINDOW_DAYS`: 20 (how far back to look)
- `LLM_BATCH_SIZE`: 10 (articles per LLM call)
- `USE_GOOGLE_SEARCH`: False (disabled, enable only with API key)
