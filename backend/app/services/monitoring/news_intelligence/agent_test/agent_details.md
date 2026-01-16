### 1. agent.py — Main orchestrator

Purpose: Entry point that runs the pipeline.

Key functions:

-   run_agent(): Orchestrates all 7 steps

-   filter_by_time_window(): Filters articles by publication date

-   get_urls_from_sources(): Gets URLs from predefined sources

-   main(): CLI entry point

Pipeline steps:

1.  Generate search queries (LLM)

1.  Search for URLs (search engine + predefined sources)

1.  Scrape article content

1.  Extract metadata

1.  Filter by time window

1.  Score relevance and filter by threshold

1.  Write to JSONL (with deduplication)

### 2. config.py — Configuration

Purpose: Centralized configuration.

Sections:

-   LLM config: Groq API settings, model, rate limiting

-   Predefined sources: 10 supply chain news websites

-   Search topics: 54 topics (disruptions, natural disasters, strikes, shortages)

-   Keywords: 80+ keywords for LLM relevance scoring

-   Output config: File paths, time windows

-   Web scraping config: Timeouts, retries, delays

-   Search engine config: Google Search API/library settings

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

Example: Topics like "port closure", "supply chain disruption" → Queries like "port closure Los Angeles 2026", "supply chain disruption Red Sea"

### 4. search_engine.py — URL discovery

Purpose: Finds URLs via search engines.

Key components:

-   SearchEngine interface: Base class

-   GoogleCustomSearchEngine: Uses Google Custom Search API (if API key provided)

-   GoogleSearchLibraryEngine: Uses googlesearch-python library (free, rate-limited)

-   create_search_engine(): Factory function that selects appropriate engine

-   search_urls(): Executes multiple queries and returns unique URLs

How it works:

-   Tries Google Custom Search API first (if credentials in .env)

-   Falls back to googlesearch-python library

-   Executes each query with rate limiting

-   Returns deduplicated list of URLs

### 5. web_scraper.py — Content scraping

Purpose: Scrapes HTML content from URLs.

Key components:

-   WebScraper class: Handles HTTP requests and HTML parsing

-   _fetch_html(): Fetches HTML with retries and exponential backoff

-   _extract_title(): Extracts title using multiple CSS selectors

-   _extract_content(): Extracts main article content

-   scrape_urls(): Batch scraping function

How it works:

-   Uses requests  + BeautifulSoup with lxml parser

-   Tries multiple CSS selectors for title/content (handles different site structures)

-   Rate limiting between requests

-   Returns dictionary with title, content, html

### 6.  metadata_extractor.py — Metadata extraction

Purpose: Extracts structured metadata from scraped content.

Key components:

-   MetadataExtractor class: Extracts metadata fields

-   _extract_publisher(): Finds author/publisher from meta tags or HTML

-   _extract_published_date(): Parses dates from meta tags or content

-   extract(): Main extraction function

How it works:

-   Parses HTML with BeautifulSoup

-   Extracts: title,  url, source (domain), publisher, published_date, content, scraped_at

-   Uses  dateparser for flexible date parsing

-   Falls back to scraped_at if no published date found

### 7. relevance_scorer.py — LLM relevance scoring

Purpose: Scores articles for relevance using LLM.

Key components:

-   RelevanceScorer class: Wraps LLMFilter

-   score_articles(): Scores articles in batches

-   filter_by_threshold(): Filters by relevance threshold

-   score_and_filter_articles(): Convenience function

How it works:

-   Reuses LLMFilter pattern from other_rss module

-   Batches articles (default: 10 per batch)

-   Sends to Groq LLM with keywords and article content

-   LLM returns relevance scores (0.0-1.0) for each article

-   Filters articles below threshold (default: 0.7)

### 8. output_handler.py — Output & deduplication

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

-   Filters new articles against existing URLs

-   Only writes unique articles

-   Logs how many duplicates were filtered

### 9. schemas.py — Data models

Purpose: Defines data structures.

Key components:

-   ScrapedArticle dataclass: Represents a scraped article with all metadata fields

-   to_dict(): Converts to dictionary for JSON serialization
