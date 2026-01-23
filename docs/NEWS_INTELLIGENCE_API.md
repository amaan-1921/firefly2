# News Intelligence API Documentation

## Overview

The News Intelligence API provides real-time access to scraped news articles formatted as MonitoringSignal objects. This API bridges the news scraping pipeline with the frontend, enabling seamless integration of supply chain-related news articles into the alerts system.

Each article from the `scraped_articles.jsonl` file is exposed as an individual NEWS_RISK signal with full article context, relevance scoring, and source attribution. The API reads fresh data on each request, ensuring the frontend always has the latest articles available.

## Architecture

The News Intelligence module consists of three key components:

**Signal Converter** (`signal_converter.py`)
- Reads articles from `scraped_articles.jsonl` in real-time
- Transforms each article into a `ScrapedArticleSignal` object
- Applies relevance filtering and sorting

**Router** (`router.py`)
- Exposes FastAPI endpoints for article retrieval
- Handles query parameters for filtering, pagination, and sorting
- Returns responses wrapped in `ArticlesResponse` metadata

**Schemas** (`schemas.py`)
- Defines `ScrapedArticleSignal` Pydantic model
- Compatible with existing alerts module signal structures
- Ensures type safety and validation

## Data Model

### ScrapedArticleSignal

Each signal object contains:

```json
{
  "signalId": "unique_md5_hash",
  "title": "Article headline",
  "sourceReference": "https://article-url.com",
  "source": "www.domain.com",
  "publishedDate": "2026-01-21T00:00:00",
  "content": "Full article text...",
  "confidenceScore": 0.9,
  "evidence": "Brief explanation of relevance",
  "scrapedAt": "2026-01-22T07:25:32.258520",
  "timestamp": "2026-01-23T10:20:25.458951"
}
```

Field Descriptions:

| Field             | Type              | Description                                                       |
| ----------------- | ----------------- | ----------------------------------------------------------------- |
| `signalId`        | string            | MD5 hash of the article URL used for unique identification        |
| `title`           | string            | Article headline                                                  |
| `sourceReference` | string            | Full URL to the original article for frontend linking             |
| `source`          | string            | Publisher or domain source, for example `www.supplychaindive.com` |
| `publishedDate`   | string (ISO 8601) | Original publication date from article metadata                   |
| `content`         | string            | Full article body text                                            |
| `confidenceScore` | float (0.0–1.0)   | LLM-assessed relevance score for supply chain topics              |
| `evidence`        | string            | Brief explanation of why the article is considered relevant       |
| `scrapedAt`       | string (ISO 8601) | Timestamp indicating when the article was scraped                 |
| `timestamp`       | string (ISO 8601) | UTC timestamp indicating when the signal was created              |

## API Endpoints

### GET /monitoring/news-intelligence/articles

Retrieve paginated list of news articles as MonitoringSignal objects.

**Query Parameters:**

- `min_relevance_score` (float, optional): Filter articles by minimum relevance score
  - Range: 0.0 to 1.0
  - Default: 0.0
  - Example: `?min_relevance_score=0.7`

- `limit` (integer, optional): Maximum number of articles to return
  - Minimum: 1
  - Default: None (return all)
  - Example: `?limit=10`

- `sort_by` (string, optional): Sorting order for results
  - Valid values:
    - `relevance_score_desc` (default): Highest to lowest relevance
    - `relevance_score_asc`: Lowest to highest relevance
    - `published_date_desc`: Most recent first
    - `published_date_asc`: Oldest first
    - `scraped_at_desc`: Most recently scraped first
  - Example: `?sort_by=published_date_desc`

**Response Format:**

```json
{
  "count": 10,
  "articles": [
    { "signalId": "...", "title": "...", ... }
  ],
  "lastUpdated": "2026-01-23T10:20:25.458951",
  "filters": {
    "minRelevanceScore": 0.7,
    "limit": 10,
    "sortBy": "relevance_score_desc"
  }
}
```

**Status Codes:**

- 200 OK: Successfully returned articles
- 422 Unprocessable Entity: Invalid query parameters

**Example Requests:**

```bash
# Get all articles sorted by relevance (highest first)
curl "http://localhost:8000/monitoring/news-intelligence/articles"

# Get top 5 most relevant articles
curl "http://localhost:8000/monitoring/news-intelligence/articles?limit=5&sort_by=relevance_score_desc"

# Get articles with relevance score above 0.8, sorted by date
curl "http://localhost:8000/monitoring/news-intelligence/articles?min_relevance_score=0.8&sort_by=published_date_desc"

# Get 20 most recent articles
curl "http://localhost:8000/monitoring/news-intelligence/articles?limit=20&sort_by=scraped_at_desc"
```

### GET /monitoring/news-intelligence/articles/count

Get total count of articles matching given filters.

Useful for pagination calculations on the frontend without retrieving full article data.

**Query Parameters:**

- `min_relevance_score` (float, optional): Filter articles by minimum relevance score
  - Default: 0.0

**Response Format:**

```json
{
  "total": 45,
  "filters": {
    "minRelevanceScore": 0.7
  },
  "lastUpdated": "2026-01-23T10:20:30.123456"
}
```

**Example Requests:**

```bash
# Total article count
curl "http://localhost:8000/monitoring/news-intelligence/articles/count"

# Count articles with relevance >= 0.8
curl "http://localhost:8000/monitoring/news-intelligence/articles/count?min_relevance_score=0.8"
```

## Running the API Server

### Prerequisites

- Python 3.10 or higher
- Virtual environment activated: `source /mnt/OldVolume/internship/firefly2/venv/bin/activate.fish`
- All dependencies installed from `requirements.txt`

### Starting the Server





# Activate virtual environment (if not already activated)

From the backend directory:

# Start the server

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start and display:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Server Configuration

- **Host**: 0.0.0.0 (accessible from any network interface)
- **Port**: 8000
- **CORS**: Enabled for all origins (development mode)
- **Auto-reload**: Disabled by default (add `--reload` flag to enable during development)

## Testing Endpoints

### Using curl

```bash
# Test root endpoint (lists all available endpoints)
curl http://localhost:8000/

# Test articles endpoint
curl "http://localhost:8000/monitoring/news-intelligence/articles?limit=2"

# Test with filters and sorting
curl "http://localhost:8000/monitoring/news-intelligence/articles?min_relevance_score=0.8&limit=5&sort_by=published_date_desc"

# Test count endpoint
curl "http://localhost:8000/monitoring/news-intelligence/articles/count?min_relevance_score=0.8"
```


## Interactive API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces provide:
- Complete endpoint documentation
- Try-it-out functionality
- Request/response examples
- Parameter validation


Each line in the JSONL file contains a complete article object with:
- Title, URL, publisher, publication date
- Full article content (scraped via BeautifulSoup)
- Relevance score (assessed by LLM against supply chain keywords)
- Scraping timestamp

The API reads this file fresh on each request, ensuring the latest data is always served.

## Integration with Alerts Module

News Intelligence signals integrate seamlessly with the existing Alerts Module:

1. Articles are formatted as `MonitoringSignal` objects with:
   - `signalType`: NEWS_RISK
   - `sourceType`: NEWS_AGENT
   - `sourceReference`: Article URL

2. Frontend can consume these signals and:
   - Display articles with full context (title, content, source)
   - Link directly to original articles via `sourceReference`
   - Filter by relevance threshold
   - Sort by publication date or relevance

3. Signals can be fed into the alerts pipeline for:
   - Grouping by affected entities (PO, supplier, region)
   - Combining with other signal types (weather, delays, supplier performance)
   - Generating prioritized alerts

## Error Handling

The API handles the following gracefully:

**Missing Data File**
- If `scraped_articles.jsonl` doesn't exist, returns empty articles list
- Status: 200 OK with count: 0

**Malformed JSON Lines**
- Skips malformed lines with warning logs
- Continues processing remaining lines
- Returns valid articles only

**Invalid Query Parameters**
- Returns 422 Unprocessable Entity with detailed error messages
- Examples:
  - `sort_by` parameter with invalid value
  - `min_relevance_score` outside 0.0-1.0 range
  - `limit` parameter with value less than 1

## Performance Considerations

- **Fresh reads**: Each request reads from disk, ensuring latest data
- **No caching**: By design, no in-memory caching (see configuration options below)
- **Sorting overhead**: Sorting is performed in-memory after loading
- **Large result sets**: Use `limit` parameter to paginate results

For high-frequency requests, consider:
1. Implementing client-side caching with reasonable TTL
2. Using `limit` parameter to reduce payload size
3. Filtering by `min_relevance_score` to reduce result set

## Configuration Options

Future enhancements could include:

1. **Caching Strategy**: Optional in-memory caching with configurable TTL
2. **Database Backend**: Migrate from JSONL to SQLite/PostgreSQL for better query performance
3. **Async File I/O**: Use aiofiles for non-blocking file reads
4. **Pagination Cursor**: Implement cursor-based pagination for large datasets
5. **Elasticsearch Integration**: Index articles for full-text search capabilities

## Troubleshooting

**Server fails to start with ModuleNotFoundError**
- Ensure virtual environment is activated
- Confirm working directory is `/mnt/OldVolume/internship/firefly2/backend`
- Verify all dependencies installed: `pip install -r requirements.txt`

**Articles endpoint returns empty list**
- Check if `scraped_articles.jsonl` file exists at expected path
- Verify JSONL file contains properly formatted JSON lines
- Run news intelligence pipeline to generate articles

**Unexpected relevance scores**
- Scores are determined by LLM assessment of article content
- Lower scores indicate less direct relevance to supply chain keywords
- Use `min_relevance_score` filter if only high-confidence articles needed

**Deprecation warnings**
- Current warnings are related to FastAPI pattern parameter naming
- No functional impact, can be safely ignored
- Will be resolved in FastAPI updates

## Related Documentation

- [Alerts Module Architecture](architecture.md)
- [Signal Pipeline Flow](flow.md)
- [Complete Alerts Implementation](ALERTS_COMPLETE.md)
- [Implementation Changes Summary](IMPLEMENTATION_CHANGES_SUMMARY.md)

## Contact and Support

For issues, questions, or enhancement requests regarding the News Intelligence API, refer to the main project documentation or contact the development team.
