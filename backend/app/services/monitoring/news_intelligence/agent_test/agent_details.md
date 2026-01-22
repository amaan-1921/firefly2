### 1. agent.py — Main orchestrator

Purpose: Entry point that runs the pipeline.

Key functions:

-   run_agent(): Orchestrates all 7 steps

-   filter_by_time_window(): Filters articles by publication date

-   main(): CLI entry point

Pipeline steps:

1.  Generate search queries (LLM)

1.  Fetch URLs from RSS feeds (primary) + search engine (optional, can be adjusted in config file- USE GOOGLE SEARCH)

1.  Scrape article content

1.  Extract metadata

1.  Filter by time window

1.  Score relevance and filter by threshold

1.  Write to JSONL (with deduplication)

**Recent Changes:**
- Now uses **RSS feeds as primary source** for articles (no rate-limiting)
- Google search moved to secondary/optional source (disabled by default)
- RSS feeds provide 50+ fresh articles per source automatically

### 2. config.py — Configuration

Purpose: Centralized configuration.

Sections:

-   LLM config: Groq API settings, model, rate limiting

-   Predefined sources: 10 supply chain news websites

-   Search topics: 63 topics (supply chain, natural disasters, strikes, shortages, **political/geopolitical**)

-   Keywords: 97 keywords for LLM relevance scoring, including **tariffs, trade wars, sanctions, geopolitical**

-   Output config: File paths, time windows

-   Web scraping config: Timeouts, retries, delays, **enhanced browser headers**

-   Search engine config: RSS feeds enabled, Google search disabled by default

**Recent Changes:**
- Added **political keywords** (tariff, trade war, embargo, sanction, regulation, policy)
- Added **geopolitical keywords** (conflict, tensions, international relations)
- Added **political search topics** (trade tariff, trade sanctions, etc.)
- Disabled Google search by default (`USE_GOOGLE_SEARCH = False`)
- Enhanced web scraper headers to bypass 403 Forbidden errors

### 3. query_generator.py — LLM query generation

Purpose: Uses LLM to generate targeted search queries.

Key components:

-   QueryGenerator class: Wraps OpenAI client for Groq

-   generate_queries(): Takes topics, returns specific search queries

How it works:

-   Takes SEARCH_TOPICS from config

-   Sends prompt to LLM with topics and current date

-   LLM generates 5-10 specific, actionable queries

-   Returns list of query strings

Example: Topics like "port closure", "trade tariff" → Queries like "port closure impact 2026", "US trade tariff 2026"

### 4. rss_fetcher.py — RSS feed aggregation (**NEW**)

Purpose: Fetches articles from RSS feeds without rate-limiting.

Key components:

-   RSSFetcher class: Parses RSS feeds using feedparser

-   fetch_feed(): Fetches articles from a single RSS feed

-   fetch_from_rss_feeds(): Batch fetches from multiple sources

-   SUPPLY_CHAIN_RSS_FEEDS: Dict mapping source names to RSS URLs

How it works:

-   Uses feedparser library to parse RSS feeds

-   Fetches up to 50 articles per feed per run

-   Extracts URL, title, published date from feed entries

-   No rate-limiting or anti-bot detection

-   Returns deduplicated list of article URLs

**Why RSS feeds:**
- No rate-limiting (designed for automated consumption)
- Fresh content (auto-updates)
- More articles (50+ per source vs 0-10 from Google search)
- Reliable (standard news infrastructure)

### 5. search_engine.py — URL discovery (search fallback)

Purpose: Finds URLs via search engines (optional/fallback).

Key components:

-   SearchEngine interface: Base class

-   GoogleCustomSearchEngine: Uses Google Custom Search API (if API key provided)

-   GoogleSearchLibraryEngine: Uses googlesearch-python library (free, rate-limited)

-   create_search_engine(): Factory function that selects appropriate engine

-   search_urls(): Executes multiple queries and returns unique URLs

How it works:

-   Tries Google Custom Search API first (if credentials in .env)

-   Falls back to googlesearch-python library

-   **Fixed API parameters**: Uses `num_results` and `sleep_interval` (was incorrectly using `num` and `stop`)

-   Executes each query with rate limiting

-   Returns deduplicated list of URLs

**Recent Changes:**
- Fixed googlesearch library API call (correct parameter names)
- Moved to optional/secondary source (agent uses RSS feeds first)

### 6. web_scraper.py — Content scraping

Purpose: Scrapes HTML content from URLs.

Key components:

-   WebScraper class: Handles HTTP requests and HTML parsing

-   _fetch_html(): Fetches HTML with retries and exponential backoff

-   _extract_title(): Extracts title using multiple CSS selectors

-   _extract_content(): Extracts main article content

-   scrape_urls(): Batch scraping function

How it works:

-   Uses requests + BeautifulSoup with lxml parser

-   Tries multiple CSS selectors for title/content (handles different site structures)

-   Rate limiting between requests

-   Returns dictionary with title, content, html

**Recent Changes:**
- Enhanced HTTP headers to look like real browser (bypasses 403 Forbidden errors)
- Added headers: Accept-Encoding, DNT, Connection, Referer, Sec-Fetch-*, Cache-Control

### 7. metadata_extractor.py — Metadata extraction

Purpose: Extracts structured metadata from scraped content.

Key components:

-   MetadataExtractor class: Extracts metadata fields

-   _extract_publisher(): Finds author/publisher from meta tags or HTML

-   _extract_published_date(): Parses dates from meta tags or content

-   extract(): Main extraction function

How it works:

-   Parses HTML with BeautifulSoup

-   Extracts: title, url, source (domain), publisher, published_date, content, scraped_at

-   Uses dateparser for flexible date parsing

-   Falls back to scraped_at if no published date found

### 8. relevance_scorer.py — LLM relevance scoring

Purpose: Scores articles for relevance using LLM.

Key components:

-   RelevanceScorer class: Wraps LLMFilter

-   score_articles(): Scores articles in batches

-   filter_by_threshold(): Filters by relevance threshold

-   score_and_filter_articles(): Convenience function

How it works:

-   Reuses LLMFilter pattern from other_rss module

-   Batches articles (default: 10 per batch)

-   Sends to Groq LLM with **97 keywords** and article content

-   LLM returns relevance scores (0.0-1.0) for each article

-   Filters articles below threshold (default: 0.7)

**Recent Changes:**
- Now includes **political/geopolitical keywords** (tariffs, trade wars, sanctions, conflicts)
- Better coverage of all supply chain disruption types

### 9. output_handler.py — Output & deduplication

Purpose: Writes articles to JSONL with deduplication.

Key components:

-   normalize_url(): Normalizes URLs for comparison (lowercase, remove trailing slash)

-   read_existing_urls(): Reads all existing URLs from JSONL file

-   filter_unique_articles(): Filters out duplicates based on URL

-   write_articles_jsonl(): Low-level JSONL writing

-   write_scraped_articles(): High-level function with deduplication

How it works:

-   When appending, reads existing URLs from file

-   Normalizes URLs (handles case differences, trailing slashes)

-   Filters new articles against existing URLs AND within-batch duplicates

-   Only writes unique articles

-   Logs how many duplicates were filtered

**Recent Changes:**
- **Fixed critical bug**: Removed mutation of `existing_urls` set that was causing false positives
- Now uses separate `seen_in_batch` set for within-batch deduplication
- Prevents non-duplicate articles from being filtered out

### 10. schemas.py — Data models

Purpose: Defines data structures.

Key components:

-   ScrapedArticle dataclass: Represents a scraped article with all metadata fields

-   to_dict(): Converts to dictionary for JSON serialization
