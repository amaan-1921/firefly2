# Alerts Module - API Reference

## Overview

The Alerts Module exposes REST endpoints via FastAPI for triggering the alerts pipeline and retrieving generated alerts.

---

## Endpoints

### GET /alerts/run-mock

Execute the complete alerts pipeline using mock data.

**Description**:
Processes 5 mock monitoring signals through all pipeline layers (Ingestion → Aggregation → Qualification → Prioritization → Context Builder) and returns generated alerts.

**Method**: GET
**Path**: `/alerts/run-mock`
**Content-Type**: application/json

#### Request

```bash
curl -X GET http://localhost:8000/alerts/run-mock
```

#### Response

**Status Code**: 200 OK

**Body** (JSON Array of Alert objects):
```json
[
  {
    "alertId": "ALERT-DB868649",
    "title": "⚠️ Weather Disruption Risk - Region: CHENNAI",
    "summary": "Alert Summary:\n🟠 Severe thunderstorm warning issued for Chennai region...",
    "priority": "P1",
    "confidenceScore": 0.92,
    "relatedSignals": [
      "WEATHER_DISRUPTION"
    ],
    "createdAt": "2025-01-22T10:30:45.123456"
  },
  {
    "alertId": "ALERT-130FF737",
    "title": "⚠️ Delivery Delay Risk - Purchase Order PO-123",
    "summary": "Alert Summary:\n• 🟡 Supplier port delays detected...",
    "priority": "P2",
    "confidenceScore": 0.865,
    "relatedSignals": [
      "PO_DELAY_RISK"
    ],
    "createdAt": "2025-01-22T10:30:45.654321"
  }
]
```

#### Response Schema

Each alert object contains:

| Field | Type | Description |
|-------|------|-------------|
| `alertId` | string | Unique alert identifier (format: ALERT-XXXXXXXX) |
| `title` | string | Concise alert title with emoji |
| `summary` | string | Detailed explanation with evidence and recommendations |
| `priority` | string | Priority level: P1 (High) / P2 (Medium) / P3 (Low) |
| `confidenceScore` | float | Average confidence (0.0 to 1.0) |
| `relatedSignals` | array | List of signal types involved |
| `createdAt` | string | ISO 8601 timestamp |

#### Error Response

**Status Code**: 500 Internal Server Error

```json
{
  "detail": "Pipeline execution failed: [error message]"
}
```

---

## Integration Examples

### Python Requests
```python
import requests

response = requests.get('http://localhost:8000/alerts/run-mock')
alerts = response.json()

for alert in alerts:
    print(f"[{alert['priority']}] {alert['title']}")
    print(f"Confidence: {alert['confidenceScore']:.0%}")
    print(alert['summary'])
    print()
```

### JavaScript/Fetch
```javascript
fetch('http://localhost:8000/alerts/run-mock')
  .then(response => response.json())
  .then(alerts => {
    alerts.forEach(alert => {
      console.log(`[${alert.priority}] ${alert.title}`);
      console.log(`Confidence: ${(alert.confidenceScore * 100).toFixed(0)}%`);
      console.log(alert.summary);
    });
  })
  .catch(error => console.error('Error:', error));
```

### cURL
```bash
# Get all alerts
curl -X GET http://localhost:8000/alerts/run-mock

# Pretty print JSON
curl -X GET http://localhost:8000/alerts/run-mock | jq .

# Show just alert titles and priorities
curl -X GET http://localhost:8000/alerts/run-mock | jq '.[] | {priority, title}'
```

### Python with FastAPI TestClient
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.get("/alerts/run-mock")
assert response.status_code == 200

alerts = response.json()
print(f"Generated {len(alerts)} alerts")
for alert in alerts:
    print(f"  - {alert['title']}")
```

---

## FastAPI Integration

To integrate the Alerts Module router into your main FastAPI application:

### Basic Integration
```python
from fastapi import FastAPI
from app.services.alerts.api import router as alerts_router

app = FastAPI(title="My App")

# Include alerts router
app.include_router(alerts_router)

# Now available at:
# GET /alerts/run-mock
```

### With Custom Prefix
```python
app.include_router(
    alerts_router,
    prefix="/api/v1"  # Endpoints: /api/v1/alerts/run-mock
)
```

### With Tags (for API docs)
```python
app.include_router(
    alerts_router,
    tags=["monitoring"]  # Groups in Swagger UI
)
```

---

## Response Examples

### Example 1: Weather Alert (P1)
```json
{
  "alertId": "ALERT-ABC123",
  "title": "⚠️ Weather Disruption Risk - Region: CHENNAI",
  "summary": "Alert Summary:\n🟠 Severe thunderstorm warning issued for Chennai region. Wind speeds expected to reach 40-50 km/h with heavy rainfall. (Impact window: 6 hours)\n\nThis affects the chennai region.\n\nRecommendation: Review related orders and consider contingency plans.",
  "priority": "P1",
  "confidenceScore": 0.92,
  "relatedSignals": ["WEATHER_DISRUPTION"],
  "createdAt": "2025-01-22T10:30:00"
}
```

### Example 2: PO Delay Alert (P2)
```json
{
  "alertId": "ALERT-XYZ789",
  "title": "⚠️ Delivery Delay Risk - Purchase Order PO-123",
  "summary": "Alert Summary:\n• 🟡 Supplier port delays detected. Expected delivery is at risk due to port congestion in Chennai. (Impact window: 2 days)\n• 🟠 Updated: Supplier forecast shows 2-3 day delay due to weather impact on production facility in Chennai. (Impact window: 3 days)\n\nThis affects the procurement for PO-123.\n\nRecommendation: Review related orders and consider contingency plans.",
  "priority": "P2",
  "confidenceScore": 0.865,
  "relatedSignals": ["PO_DELAY_RISK"],
  "createdAt": "2025-01-22T10:30:00"
}
```

---

## Priority Levels

### P1 (High Urgency)
**When Triggered**:
- CRITICAL severity + confidence ≥ 75%
- HIGH severity + confidence ≥ 85%
- Impact within 6 hours + confidence ≥ 80%

**Action Required**: Immediate review and response

**Example**: Severe weather affecting active shipments

### P2 (Medium Urgency)
**When Triggered**:
- HIGH severity + confidence ≥ 70%
- MEDIUM severity + confidence ≥ 85%
- Impact within 6 hours + confidence ≥ 70%

**Action Required**: Review within hours, plan contingency

**Example**: Supplier performance declining, forecast delays

### P3 (Low Urgency)
**When Triggered**:
- All other qualifying signals

**Action Required**: Monitor and adjust plans as needed

**Example**: Minor supplier issues, low confidence warnings

---

## Confidence Scores

Alerts include a `confidenceScore` (0.0 to 1.0) representing confidence in the alert:

| Score | Interpretation |
|-------|-----------------|
| 0.9+ | Very High (critical signal) |
| 0.8-0.89 | High (strong evidence) |
| 0.7-0.79 | Medium (multiple corroborating signals) |
| 0.6-0.69 | Low (some evidence) |
| < 0.6 | Very Low (insufficient evidence) |

**Alerts are only generated for**:
- Single signals with confidence ≥ 0.85, OR
- Multiple signals each with confidence ≥ 0.75

---

## Signal Types

Alerts reference the following signal types:

| Type | Source | Description |
|------|--------|-------------|
| `WEATHER_DISRUPTION` | Weather Agent | Weather-related supply chain disruption |
| `PO_DELAY_RISK` | PO Agent | Risk of purchase order delay |
| `SUPPLIER_PERFORMANCE_DROP` | Supplier Agent | Declining supplier performance metrics |
| `NEWS_RISK` | News Agent | External news affecting supply chain |

---

## Testing

### Manual Testing
```bash
# Start your FastAPI app
python -m uvicorn app.main:app --reload

# In another terminal, call the endpoint
curl http://localhost:8000/alerts/run-mock | jq .
```

### Automated Testing
```python
from fastapi.testclient import TestClient
from app.main import app

def test_run_mock_alerts():
    client = TestClient(app)
    response = client.get("/alerts/run-mock")
    
    assert response.status_code == 200
    alerts = response.json()
    
    assert len(alerts) > 0
    for alert in alerts:
        assert "alertId" in alert
        assert "title" in alert
        assert "priority" in alert
        assert alert["priority"] in ["P1", "P2", "P3"]
        assert 0 <= alert["confidenceScore"] <= 1
```

---

## Performance

- **Response Time**: ~50-100ms (mock data)
- **Throughput**: Single endpoint (not rate-limited in MVP)
- **Data Size**: ~3-5KB per response (2 alerts from mock data)

---

## Limitations (MVP)

- ✓ Uses mock data only (no real monitoring integration)
- ✓ No database persistence
- ✓ No authentication/authorization
- ✓ No rate limiting
- ✓ Single endpoint (run-mock only)
- ✓ No filtering or searching capabilities
- ✓ No alert acknowledgment or resolution tracking

---

## Future Enhancements

Planned additions:
- [ ] Custom signal ingestion (real data)
- [ ] Alert persistence and history
- [ ] Alert filtering by priority/type/entity
- [ ] Authentication and role-based access
- [ ] Webhook notifications
- [ ] Alert acknowledgment/resolution
- [ ] Batch operations
- [ ] Analytics and trending

---

## Support

For issues or questions:
1. Check [ALERTS_QUICK_START.md](ALERTS_QUICK_START.md) for common usage
2. Review [ALERTS_MODULE_IMPLEMENTATION.md](ALERTS_MODULE_IMPLEMENTATION.md) for architecture details
3. Run [test_pipeline.py](backend/app/services/alerts/test_pipeline.py) to verify installation
