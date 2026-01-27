# API Documentation - Complete Reference

Comprehensive guide to all APIs and endpoints in the Firefly2 supply chain platform, including backend FastAPI endpoints and frontend Next.js API routes.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend API (FastAPI)](#backend-api-fastapi)
3. [Frontend API Routes (Next.js)](#frontend-api-routes-nextjs)
4. [API Client Setup](#api-client-setup)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)
7. [Request/Response Examples](#requestresponse-examples)
8. [Integration Flows](#integration-flows)

---

## Architecture Overview

The application uses a **two-tier API architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Frontend API Routes (/src/app/api/)             │  │
│  │  - Acts as middleware/proxy                      │  │
│  │  - Handles auth, transformations, mock data      │  │
│  │  - Communicates with Backend                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────┘
                  │
                  │ HTTP/REST
                  │
┌─────────────────▼──────────────────────────────────────┐
│              Backend API (FastAPI)                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Alerts Module (/alerts)                        │  │
│  │  - run-mock: Pipeline with mock data            │  │
│  │  - run-from-jsonl: Pipeline with JSONL files    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  News Intelligence (/monitoring/news-...)       │  │
│  │  - articles: Get scraped news articles          │  │
│  │  - articles/count: Get article count            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Weather Risk (/monitoring/weather/...)         │  │
│  │  - check: Evaluate weather risks                │  │
│  │  - health: Service health check                 │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  System Endpoints                               │  │
│  │  - /: API info and available endpoints          │  │
│  │  - /health: Overall health check                │  │
│  │  - /docs: Swagger UI documentation              │  │
│  │  - /redoc: ReDoc documentation                  │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Key Points

- **Backend** runs on `http://localhost:8000`
- **Frontend** runs on `http://localhost:3000`
- **Middleware Integration**: Frontend API routes can proxy to backend
- **CORS Enabled**: Backend allows requests from any origin (development mode)
- **Automatic Documentation**: Backend has Swagger UI at `/docs` and ReDoc at `/redoc`

---

## Backend API (FastAPI)

### Server Configuration

**Location:** `backend/app/main.py`

```python
# Startup
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Endpoints will be available at http://localhost:8000
```

### Middleware & Configuration

**CORS Enabled** for local development:
- `allow_origins`: `["*"]` (all origins)
- `allow_credentials`: `True`
- `allow_methods`: `["*"]` (all HTTP methods)
- `allow_headers`: `["*"]` (all headers)

---

### System Endpoints

#### 1. Root Endpoint

**GET** `/`

Returns general API information and available endpoints.

**Response:**
```json
{
  "message": "Alerts Module API",
  "version": "1.0.0",
  "endpoints": {
    "alerts": {
      "mock_alerts": "/alerts/run-mock",
      "jsonl_alerts": "/alerts/run-from-jsonl"
    },
    "news_intelligence": {
      "articles": "/monitoring/news-intelligence/articles",
      "articles_count": "/monitoring/news-intelligence/articles/count"
    }
  }
}
```

**Status Codes:**
- `200 OK`: Successful response

---

#### 2. Health Check

**GET** `/health`

Simple health check endpoint to verify server is running.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK`: Server is healthy

**Usage:**
- Monitor server availability
- Liveness probe for container orchestration

---

#### 3. Swagger UI

**GET** `/docs`

Interactive API documentation with **try-it-out** functionality.

**Features:**
- View all endpoints with descriptions
- Test endpoints directly in browser
- See request/response schemas
- Auto-generated from code docstrings

---

#### 4. ReDoc Documentation

**GET** `/redoc`

Alternative API documentation format (read-only).

**Features:**
- Clean, readable documentation layout
- Better for sharing with non-technical stakeholders
- Organized by tags

---

### Alerts Module Endpoints

**Prefix:** `/alerts`

**Tag:** `alerts`

#### 1. Run Mock Pipeline

**GET** `/alerts/run-mock`

Execute the complete alerts pipeline using mock signals for testing.

**Response Model:** `List[Alert]`

**Response Example:**
```json
[
  {
    "alertId": "ALERT-A1B2C3D4",
    "title": "Weather Disruption Risk - Region: Chennai",
    "summary": "Severe thunderstorm warning issued for Chennai region...",
    "priority": "P1",
    "confidenceScore": 0.92,
    "relatedSignals": ["WEATHER_DISRUPTION"],
    "createdAt": "2024-01-24T10:30:00"
  },
  {
    "alertId": "ALERT-X9Y8Z7W6",
    "title": "Delivery Delay Risk - Purchase Order PO-123",
    "summary": "Supplier port delays detected...",
    "priority": "P2",
    "confidenceScore": 0.85,
    "relatedSignals": ["PO_DELAY_RISK"],
    "createdAt": "2024-01-24T10:30:00"
  }
]
```

**Status Codes:**
- `200 OK`: Pipeline executed successfully
- `500 Internal Server Error`: Pipeline execution failed

**Use Cases:**
- Development and testing
- Demonstrating alert generation
- Validating pipeline logic without real data

**Internal Flow:**
1. Load mock signals from `mock_data.py`
2. Run through all pipeline stages
3. Return generated alerts

---

#### 2. Run JSONL Pipeline

**GET** `/alerts/run-from-jsonl`

Execute the complete alerts pipeline using JSONL data files (production mode).

**Query Parameters:** (Optional)
- `weather_file_path`: Custom path to weather signals JSONL
  - Default: `app/services/monitoring/weather_risk/weather_output.jsonl`
- `news_file_path`: Custom path to news signals JSONL
  - Default: `app/services/monitoring/news_intelligence/agent_test/scraped_articles.jsonl`

**Response Model:** `List[Alert]`

**Response Example:**
```json
[
  {
    "alertId": "ALERT-K1L2M3N4",
    "title": "Weather Disruption Risk - Region: Chennai",
    "summary": "Severe thunderstorm warning issued...",
    "priority": "P1",
    "confidenceScore": 0.92,
    "relatedSignals": ["WEATHER_DISRUPTION"],
    "createdAt": "2024-01-24T10:35:22"
  }
]
```

**Status Codes:**
- `200 OK`: Pipeline executed successfully (even if no signals found)
- `500 Internal Server Error`: File read or processing error

**Error Handling:**
- Missing files return empty alerts list instead of error
- Malformed JSON in JSONL is logged and skipped
- System continues with whatever valid data is available

**Use Cases:**
- Production alerts from monitoring data
- Scheduled execution via cron jobs
- Triggered by monitoring agents

**Pipeline Stages:**
1. **Ingestion** - Load signals from JSONL files
2. **Aggregation** - Group signals by entity
3. **Qualification** - Filter alert-worthy contexts
4. **Prioritization** - Assign priority levels
5. **Context Builder** - Generate human-readable alerts

---

### News Intelligence Endpoints

**Prefix:** `/monitoring/news-intelligence`

**Tag:** `news-intelligence`

#### 1. Get Articles

**GET** `/monitoring/news-intelligence/articles`

Retrieve scraped news articles as MonitoringSignal-compatible signals.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `min_relevance_score` | float | 0.0 | Filter articles by minimum relevance (0.0-1.0) |
| `limit` | integer | None | Maximum articles to return |
| `sort_by` | string | `relevance_score_desc` | Sort order |

**Sort Options:**
- `relevance_score_desc`: Highest relevance first
- `relevance_score_asc`: Lowest relevance first
- `published_date_desc`: Newest articles first
- `published_date_asc`: Oldest articles first
- `scraped_at_desc`: Most recently scraped first

**Response Model:** `ArticlesResponse`

**Response Structure:**
```json
{
  "count": 5,
  "articles": [
    {
      "signalId": "hash-of-url-1",
      "title": "Supply Chain Disruption Expected",
      "sourceReference": "https://example.com/article1",
      "source": "example.com",
      "publishedDate": "2024-01-24T09:15:00",
      "content": "Full article content here...",
      "confidenceScore": 0.85,
      "evidence": "Article discusses supply chain risks affecting manufacturing",
      "scrapedAt": "2024-01-24T10:30:00",
      "timestamp": "2024-01-24T10:30:00"
    },
    {
      "signalId": "hash-of-url-2",
      "title": "Port Workers Strike Announced",
      "sourceReference": "https://example.com/article2",
      "source": "news.com",
      "publishedDate": "2024-01-23T15:45:00",
      "content": "Port workers in Southeast Asia announce strike...",
      "confidenceScore": 0.72,
      "evidence": "Strike could impact port operations",
      "scrapedAt": "2024-01-24T10:30:00",
      "timestamp": "2024-01-24T10:30:00"
    }
  ],
  "lastUpdated": "2024-01-24T10:30:00",
  "filters": {
    "minRelevanceScore": 0.7,
    "limit": null,
    "sortBy": "relevance_score_desc"
  }
}
```

**Status Codes:**
- `200 OK`: Articles retrieved successfully
- `422 Unprocessable Entity`: Invalid query parameters

**Example Requests:**

Get top 10 most relevant articles:
```
GET /monitoring/news-intelligence/articles?min_relevance_score=0.7&limit=10&sort_by=relevance_score_desc
```

Get all articles sorted by date:
```
GET /monitoring/news-intelligence/articles?sort_by=published_date_desc
```

Get highly relevant articles only:
```
GET /monitoring/news-intelligence/articles?min_relevance_score=0.9
```

**Data Source:**
- Reads from `scraped_articles.jsonl` on each request
- Fresh data on every call (no caching at endpoint level)
- Used by alerts module as signals

**Article Fields:**
- `signalId`: Hash of URL for unique identification
- `title`: Article headline
- `sourceReference`: Full URL to article
- `source`: Domain/publication name
- `publishedDate`: When article was published
- `content`: Full article text
- `confidenceScore`: Relevance score (0.0-1.0) calculated during scraping
- `evidence`: Brief explanation of why article is relevant
- `scrapedAt`: When article was scraped/added

---

#### 2. Get Articles Count

**GET** `/monitoring/news-intelligence/articles/count`

Get total count of articles matching filters without retrieving full data.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `min_relevance_score` | float | 0.0 | Filter articles by minimum relevance |

**Response:**
```json
{
  "total": 42,
  "filters": {
    "minRelevanceScore": 0.7
  },
  "lastUpdated": "2024-01-24T10:30:00"
}
```

**Status Codes:**
- `200 OK`: Count retrieved successfully
- `422 Unprocessable Entity`: Invalid query parameters

**Use Cases:**
- Pagination calculation on frontend
- Checking if articles exist
- Monitoring data freshness

---

### Weather Risk Endpoints

**Prefix:** `/monitoring/weather`

**Tag:** `weather-risk`

#### 1. Check Weather Risks

**POST** `/monitoring/weather/check`

Manually trigger weather risk evaluation for all monitored locations.

**Request Body:**
```
Empty (POST endpoint but no request body required)
```

**Response Model:** `WeatherCheckResponse`

**Response Example:**
```json
{
  "signals": [
    {
      "signalType": "WEATHER_DISRUPTION",
      "sourceType": "WEATHER_AGENT",
      "sourceReference": "Chennai",
      "severityLevel": "HIGH",
      "confidenceScore": 0.92,
      "expectedImpactWindow": "6 hours",
      "evidence": "Severe thunderstorm warning for Chennai region",
      "timestamp": "2024-01-24T10:30:00"
    },
    {
      "signalType": "WEATHER_DISRUPTION",
      "sourceType": "WEATHER_AGENT",
      "sourceReference": "Mumbai",
      "severityLevel": "MEDIUM",
      "confidenceScore": 0.75,
      "expectedImpactWindow": "1 day",
      "evidence": "Heavy rainfall expected in Mumbai",
      "timestamp": "2024-01-24T10:30:00"
    }
  ],
  "locationCount": 10,
  "timestamp": "2024-01-24T10:30:00"
}
```

**Status Codes:**
- `200 OK`: Weather evaluation completed successfully
- `500 Internal Server Error`: Weather data fetch or processing failed

**Endpoint Behavior:**
- Does NOT write to database
- Does NOT send notifications
- Returns raw MonitoringSignal objects for further processing
- Intended for orchestration/manual triggers

**Use Cases:**
- Manual trigger for weather risk evaluation
- Scheduled checks via external cron job
- Debugging weather agent integration

---

#### 2. Weather Health Check

**GET** `/monitoring/weather/health`

Health check endpoint for the Weather Risk Agent service.

**Response:**
```json
{
  "status": "healthy",
  "service": "weather-risk-agent",
  "timestamp": "2024-01-24T10:30:00"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

**Use Cases:**
- Monitor service availability
- Liveness checks in container orchestration

---

## Frontend API Routes (Next.js)

### Architecture

Frontend API routes are located in `src/app/api/` and act as **middleware** between the frontend and backend.

**Responsibilities:**
- Call backend APIs
- Transform data to frontend schema
- Handle authentication
- Provide mock data if backend unavailable
- Centralize API calling logic

---

### Alerts Route

**File:** `frontend/src/app/api/alerts/route.ts`

#### GET /api/alerts

Fetch alerts from backend and transform to frontend schema.

**Frontend Endpoint:**
```
GET http://localhost:3000/api/alerts
```

**Backend Call:**
```
GET http://localhost:8000/alerts/run-from-jsonl
```

**Response Transformation:**

Backend Alert → Frontend Alert:

```
Backend Alert:
{
  "alertId": "ALERT-A1B2C3D4",
  "title": "Weather Disruption Risk - Region: Chennai",
  "summary": "Severe thunderstorm warning...",
  "priority": "P1",
  "relatedSignals": ["WEATHER_DISRUPTION"],
  "createdAt": "2024-01-24T10:30:00",
  "confidenceScore": 0.92
}

         ↓↓↓ Transformation ↓↓↓

Frontend Alert:
{
  "id": "ALERT-A1B2C3D4",
  "title": "Weather Disruption Risk - Region: Chennai",
  "description": "Severe thunderstorm warning...",
  "severity": "CRITICAL",                    // P1 → CRITICAL
  "riskCategory": "WEATHER",                 // From relatedSignals
  "impactedPoCount": 0,                      // Not in backend yet
  "estimatedRevenueImpact": 0,               // Not in backend yet
  "status": "MONITORING",                    // Hardcoded
  "source": "News Intelligence",             // Hardcoded
  "detectedAt": "2024-01-24T10:30:00",       // From createdAt
  "lastUpdatedAt": "2024-01-24T10:30:00",    // From createdAt
  "relatedPoIds": [],                        // Not in backend yet
}
```

**Priority to Severity Mapping:**

| Backend Priority | Frontend Severity |
|---|---|
| P1 | CRITICAL |
| P2 | HIGH |
| P3 | MEDIUM |

**Signal to Category Mapping:**

```typescript
function signalToCategory(signals: string[]): string {
    const signal = signals[0];
    if (signal.includes('NEWS')) return 'GEOPOLITICAL';
    if (signal.includes('WEATHER')) return 'WEATHER';
    if (signal.includes('LOGISTICS')) return 'LOGISTICS';
    if (signal.includes('SUPPLIER')) return 'SUPPLIER_PERFORMANCE';
    if (signal.includes('TARIFF')) return 'TARIFF';
    return 'OTHER';
}
```

**Response Example:**
```json
[
  {
    "id": "ALERT-A1B2C3D4",
    "title": "Weather Disruption Risk - Region: Chennai",
    "description": "Severe thunderstorm warning issued for Chennai region...",
    "severity": "CRITICAL",
    "riskCategory": "WEATHER",
    "impactedPoCount": 0,
    "estimatedRevenueImpact": 0,
    "status": "MONITORING",
    "source": "News Intelligence",
    "detectedAt": "2024-01-24T10:30:00",
    "lastUpdatedAt": "2024-01-24T10:30:00",
    "relatedPoIds": [],
    "relatedPoIds": []
  }
]
```

**Status Codes:**
- `200 OK`: Alerts retrieved and transformed
- `500 Internal Server Error`: Backend call failed

**Error Handling:**
```typescript
try {
    const res = await fetch('http://localhost:8000/alerts/run-from-jsonl')
    // Transform...
} catch (error) {
    return NextResponse.json(
        { error: 'Failed to fetch alerts' },
        { status: 500 }
    )
}
```

---

### Impact Route

**File:** `frontend/src/app/api/impact/route.ts`

#### GET /api/impact

Fetch purchase orders impacted by a specific alert.

**Frontend Endpoint:**
```
GET http://localhost:3000/api/impact?alertId=ALERT-A1B2C3D4
```

**Query Parameters:**
- `alertId` (required): The alert ID to get impact for

**Response Type:** `PO[]`

**Response Example:**
```json
[
  {
    "id": "uuid-1",
    "poNumber": "PO-567890",
    "supplierId": "uuid-supplier-1",
    "supplierName": "Acme Manufacturing",
    "item": "Electronic Control Unit",
    "quantity": 5000,
    "dueDate": "2024-02-15",
    "currency": "USD",
    "financialImpact": 750000,
    "status": "DELAYED",
    "alertIds": ["ALERT-A1B2C3D4"]
  },
  {
    "id": "uuid-2",
    "poNumber": "PO-567891",
    "supplierId": "uuid-supplier-1",
    "supplierName": "Acme Manufacturing",
    "item": "Sensor Module",
    "quantity": 10000,
    "dueDate": "2024-02-20",
    "currency": "USD",
    "financialImpact": 450000,
    "status": "DELAYED",
    "alertIds": ["ALERT-A1B2C3D4"]
  }
]
```

**Status Codes:**
- `200 OK`: Impact data retrieved
- `200 OK`: No impact data (returns empty array if no alertId)

**Current Implementation:**
- Uses mock data generation with Faker.js
- Generates 5 random POs per alert
- TODO: Connect to real backend impact calculation

**Backend Integration (Future):**
```typescript
// When backend is ready:
const res = await fetch(
  `${process.env.BACKEND_URL}/impact?alertId=${alertId}`
);
```

---

### Authentication Route

**File:** `frontend/src/app/api/auth/[...nextauth]/route.ts`

NextAuth.js authentication endpoints.

**Endpoints Exposed:**
- `POST /api/auth/signin`
- `GET /api/auth/session`
- `POST /api/auth/signout`
- `GET /api/auth/callback/...`

**Configuration:** `src/auth.ts`

**Credentials Provider:**
```
Email: user1@company.com
Password: password123
```

**Response (on successful login):**
```json
{
  "user": {
    "id": "1",
    "name": "User One",
    "email": "user1@company.com",
    "role": "manager"
  },
  "expires": "2024-01-25T10:30:00Z"
}
```

**Session Data:**
```json
{
  "user": {
    "id": "1",
    "name": "User One",
    "email": "user1@company.com",
    "role": "manager"
  },
  "expires": "2024-01-25T10:30:00Z"
}
```

---

## API Client Setup

### Frontend API Client

**File:** `frontend/src/lib/api-client.ts`

Simple Axios-based HTTP client:

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api',              // Relative to frontend
  timeout: 10000                // 10 second timeout
});
```

**Usage in Components:**
```typescript
import { apiClient } from '@/lib/api-client';

// GET request
const response = await apiClient.get<Alert[]>('/alerts');
console.log(response.data);

// POST request
const response = await apiClient.post('/impact', { alertId: 'ALERT-123' });

// With error handling
try {
  const data = await apiClient.get('/alerts');
} catch (error) {
  console.error('API call failed:', error);
}
```

### React Query Integration

**Hook:** `frontend/src/hooks/useAlerts.ts`

```typescript
export function useAlerts() {
  return useQuery<Alert[]>({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await apiClient.get<Alert[]>('/alerts');
      return res.data;
    },
    refetchInterval: 60_000,      // Auto-refresh every 60 seconds
    staleTime: 30_000,            // Data fresh for 30 seconds
    refetchOnWindowFocus: true    // Refresh when window regains focus
  });
}
```

**Usage in Components:**
```typescript
function AlertsPage() {
  const { data: alerts, isLoading, error } = useAlerts();
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {alerts?.map(alert => (
        <Alert key={alert.id} alert={alert} />
      ))}
    </div>
  );
}
```

---

## Authentication

### Next.js Auth Configuration

**Files:**
- `frontend/src/auth.ts` - Main auth configuration
- `frontend/auth.config.ts` - Auth settings
- `frontend/middleware.ts` - Route protection

### Credentials Provider

**Demo User:**
```
Email: user1@company.com
Password: password123
```

**Real Implementation:**
Replace with actual database lookup:
```typescript
async authorize(credentials) {
  // Connect to real database
  const user = await db.users.findByEmail(credentials.email);
  
  if (user && await bcrypt.compare(credentials.password, user.passwordHash)) {
    return {
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role
    };
  }
  
  return null;
}
```

### Protected Routes

Routes requiring authentication are defined in middleware:

```typescript
// Frontend routes protected by NextAuth
- /dashboard/*
- /alerts
- /monitoring
- /impact
- /recommendations
```

Public routes:
- /
- /login
- /api/auth/*

---

## Error Handling

### Backend Error Handling

**Pattern:**
```python
@router.get("/endpoint")
async def endpoint():
    try:
        # Business logic
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error description: {str(e)}"
        )
```

**Error Responses:**

500 Internal Server Error:
```json
{
  "detail": "Error description"
}
```

422 Unprocessable Entity (validation error):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["query", "min_relevance_score"],
      "msg": "ensure this value is less than or equal to 1",
      "input": "1.5"
    }
  ]
}
```

### Frontend Error Handling

**In API Routes:**
```typescript
try {
  const res = await fetch('http://localhost:8000/alerts/run-from-jsonl');
  
  if (!res.ok) {
    throw new Error(`Backend returned ${res.status}`);
  }
  
  return NextResponse.json(transformedData);
} catch (error) {
  return NextResponse.json(
    { error: 'Failed to fetch alerts' },
    { status: 500 }
  );
}
```

**In React Components:**
```typescript
const { data, error, isLoading } = useAlerts();

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
return <AlertsList alerts={data} />;
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| CORS error | Backend not started | Start backend: `python -m uvicorn app.main:app --reload` |
| 404 endpoint not found | Wrong URL path | Check capitalization and trailing slashes |
| 422 validation error | Invalid query params | Check parameter types match schema |
| 500 backend error | Missing files or data | Check JSONL files exist, readable |
| Timeout error | Slow network or backend | Increase timeout, check backend performance |

---

## Request/Response Examples

### Example 1: Get Alerts

**Frontend Component Request:**
```typescript
// In React component
const { data: alerts } = useAlerts();
```

**Actual HTTP Requests:**

Step 1: Frontend component calls `useAlerts()`
```
GET http://localhost:3000/api/alerts
Accept: application/json
```

Step 2: Frontend API route calls backend
```
GET http://localhost:8000/alerts/run-from-jsonl
```

Step 3: Backend returns raw alerts
```json
[
  {
    "alertId": "ALERT-A1B2C3D4",
    "title": "Weather Disruption Risk - Region: Chennai",
    "summary": "Severe thunderstorm warning...",
    "priority": "P1",
    "confidenceScore": 0.92,
    "relatedSignals": ["WEATHER_DISRUPTION"],
    "createdAt": "2024-01-24T10:30:00"
  }
]
```

Step 4: Frontend API transforms
```json
[
  {
    "id": "ALERT-A1B2C3D4",
    "title": "Weather Disruption Risk - Region: Chennai",
    "description": "Severe thunderstorm warning...",
    "severity": "CRITICAL",
    "riskCategory": "WEATHER",
    "impactedPoCount": 0,
    "estimatedRevenueImpact": 0,
    "status": "MONITORING",
    "source": "News Intelligence",
    "detectedAt": "2024-01-24T10:30:00",
    "lastUpdatedAt": "2024-01-24T10:30:00",
    "relatedPoIds": []
  }
]
```

Step 5: Frontend component receives transformed data
```typescript
// alerts now contains the transformed array
alerts.map(alert => <AlertCard alert={alert} />)
```

---

### Example 2: Get News Articles

**cURL Request:**
```bash
curl "http://localhost:8000/monitoring/news-intelligence/articles?min_relevance_score=0.7&limit=5&sort_by=relevance_score_desc"
```

**Response:**
```json
{
  "count": 5,
  "articles": [
    {
      "signalId": "hash-abc123",
      "title": "Supply Chain Crisis Deepens",
      "sourceReference": "https://example.com/article1",
      "source": "example.com",
      "publishedDate": "2024-01-24T09:15:00",
      "content": "Full article text...",
      "confidenceScore": 0.95,
      "evidence": "Article directly discusses supply chain disruptions",
      "scrapedAt": "2024-01-24T10:30:00",
      "timestamp": "2024-01-24T10:30:00"
    }
  ],
  "lastUpdated": "2024-01-24T10:30:00",
  "filters": {
    "minRelevanceScore": 0.7,
    "limit": 5,
    "sortBy": "relevance_score_desc"
  }
}
```

---

### Example 3: Check Weather Risks

**cURL Request:**
```bash
curl -X POST http://localhost:8000/monitoring/weather/check
```

**Response:**
```json
{
  "signals": [
    {
      "signalType": "WEATHER_DISRUPTION",
      "sourceType": "WEATHER_AGENT",
      "sourceReference": "Chennai",
      "severityLevel": "HIGH",
      "confidenceScore": 0.92,
      "expectedImpactWindow": "6 hours",
      "evidence": "Severe thunderstorm warning...",
      "timestamp": "2024-01-24T10:30:00"
    }
  ],
  "locationCount": 10,
  "timestamp": "2024-01-24T10:30:00"
}
```

---

### Example 4: Get PO Impact

**Frontend Request:**
```typescript
const response = await apiClient.get('/impact?alertId=ALERT-A1B2C3D4');
```

**HTTP Request:**
```
GET http://localhost:3000/api/impact?alertId=ALERT-A1B2C3D4
```

**Response:**
```json
[
  {
    "id": "uuid-1",
    "poNumber": "PO-567890",
    "supplierId": "uuid-supplier-1",
    "supplierName": "Acme Manufacturing",
    "item": "Electronic Control Unit",
    "quantity": 5000,
    "dueDate": "2024-02-15",
    "currency": "USD",
    "financialImpact": 750000,
    "status": "DELAYED",
    "alertIds": ["ALERT-A1B2C3D4"]
  }
]
```

---

## Integration Flows

### Complete Alert Flow

```
┌──────────────────────────────────────────────────────────┐
│ 1. Monitoring Agents (External)                          │
│    - Weather agent generates weather_output.jsonl        │
│    - News agent generates scraped_articles.jsonl         │
│    - PO agent monitors shipments                         │
│    - Supplier agent tracks performance                   │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Data Storage (JSONL Files)                            │
│    - backend/app/services/monitoring/weather_risk/...    │
│    - backend/app/services/monitoring/news_intelligence/..│
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Backend API Endpoints                                 │
│    GET /alerts/run-from-jsonl                           │
│    GET /monitoring/news-intelligence/articles            │
│    POST /monitoring/weather/check                        │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Alert Processing Pipeline                            │
│    1. Ingestion - Load & normalize signals              │
│    2. Aggregation - Group by entity                     │
│    3. Qualification - Filter alert-worthy               │
│    4. Prioritization - Assign P1/P2/P3                  │
│    5. Context Builder - Generate readable alerts        │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 5. Frontend API Middleware                              │
│    GET /api/alerts                                      │
│    - Calls backend                                      │
│    - Transforms schema                                  │
│    - Returns frontend format                            │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 6. React Components (useAlerts hook)                    │
│    - Fetch via React Query                              │
│    - Auto-refresh every 60 seconds                      │
│    - Display alerts to user                             │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 7. User Interface                                        │
│    - Alerts dashboard                                   │
│    - Alert details view                                 │
│    - Related POs impact view                            │
│    - Actions & recommendations                          │
└──────────────────────────────────────────────────────────┘
```

### Data Transformation Flow

```
Raw Signal (JSONL)
├─ Title: "Severe thunderstorm warning"
├─ Content: "Severe weather expected in Chennai..."
├─ Relevance Score: 0.92
└─ Published Date: "2024-01-24"

        ↓↓↓ Ingestion ↓↓↓

MonitoringSignal
├─ signalType: NEWS_RISK
├─ sourceType: NEWS_AGENT
├─ sourceReference: "NEWS-PUBLISHER_0"
├─ severityLevel: HIGH
├─ confidenceScore: 0.92
├─ evidence: "Title: Severe thunderstorm..."
└─ timestamp: "2024-01-24T10:30:00"

        ↓↓↓ Aggregation ↓↓↓

RiskContext
├─ contextId: "RISK-A1B2C3D4"
├─ relatedEntity: "Chennai"
└─ signals: [MonitoringSignal]

        ↓↓↓ Qualification ↓↓↓

QualifyingContext
└─ Confidence 0.92 ≥ threshold 0.7 ✓

        ↓↓↓ Prioritization ↓↓↓

RankedContext
├─ Priority: P1
└─ Reason: HIGH severity + 0.92 confidence ≥ 0.85

        ↓↓↓ Context Builder ↓↓↓

BackendAlert
├─ alertId: "ALERT-A1B2C3D4"
├─ title: "Weather Disruption Risk - Region: Chennai"
├─ summary: "Severe thunderstorm warning issued..."
├─ priority: P1
└─ confidenceScore: 0.92

        ↓↓↓ Frontend Transform ↓↓↓

FrontendAlert
├─ id: "ALERT-A1B2C3D4"
├─ title: "Weather Disruption Risk - Region: Chennai"
├─ description: "Severe thunderstorm warning issued..."
├─ severity: "CRITICAL"            (P1 → CRITICAL)
└─ riskCategory: "WEATHER"         (NEWS_RISK → WEATHER)

        ↓↓↓ React Component ↓↓↓

AlertCard
└─ Displays to user with formatting
```

### Error Handling Flow

```
API Call from Frontend
        │
        ▼
┌─────────────────────────┐
│ Frontend API Route      │
│ (/api/alerts)          │
└─────────────┬───────────┘
              │
              ▼
        Call Backend?
        │         │
        Yes      No (mock data)
        │         │
        ▼         ▼
    Backend    Mock Data
       │
       ├─ 200 OK
       │   └─ Transform & return
       │
       ├─ 404 Not Found
       │   └─ Return empty array
       │
       ├─ 500 Server Error
       │   └─ Log & return 500
       │
       └─ Network Error
           └─ Try/catch → return 500

              │
              ▼
    ┌──────────────────┐
    │ Frontend Component │
    │ useAlerts() hook  │
    └─────────┬────────┘
              │
              ├─ isLoading → Show spinner
              ├─ error → Show error message
              └─ data → Render alerts
```

---

## Summary

This comprehensive API structure provides:

✅ **Layered Architecture** - Backend processes signals, frontend transforms for UI
✅ **Flexible Data Pipeline** - Ingestion, aggregation, qualification, prioritization
✅ **Multiple Data Sources** - News, weather, PO, supplier signals
✅ **Real-time Alerts** - Auto-refresh every 60 seconds
✅ **Error Resilience** - Graceful degradation, mock data fallback
✅ **Authentication** - NextAuth with demo credentials
✅ **API Documentation** - Swagger UI and ReDoc for exploration
✅ **Type Safety** - Pydantic models (backend) and TypeScript (frontend)

The system balances **operational simplicity** (clear endpoints, consistent patterns) with **sophisticated processing** (multi-stage pipeline, intelligent filtering) to deliver actionable supply chain intelligence.

