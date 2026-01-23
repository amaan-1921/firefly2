"""
Alerts Module - Quick Start Guide
"""

# Quick Start Guide

## What Was Built

A complete MVP Alerts Module that:
- Takes monitoring signals from various agents (weather, news, PO, supplier)
- Processes them through a 5-layer pipeline
- Outputs human-readable alerts with priority levels

## Using the Module

### Option 1: Direct Python Usage

```python
from app.services.alerts import run_alerts_pipeline

# Run pipeline with mock data
alerts = run_alerts_pipeline()

# Print results
for alert in alerts:
    print(f"[{alert.priority}] {alert.title}")
    print(f"  ID: {alert.alertId}")
    print(f"  Confidence: {alert.confidenceScore:.0%}")
    print()
```

### Option 2: API Endpoint

```bash
# Start your FastAPI server
# Then curl the endpoint:

curl http://localhost:8000/alerts/run-mock | jq .

# Response is a JSON array of alerts
```

### Option 3: FastAPI Integration

```python
from fastapi import FastAPI
from app.services.alerts.api import router

app = FastAPI()
app.include_router(router)

# Endpoint available at: GET /alerts/run-mock
```

## Pipeline Stages

```
Raw Signals → Ingest → Aggregate → Qualify → Prioritize → Build Alerts
```

1. **Ingestion**: Validate & filter by source type
2. **Aggregation**: Group by entity (PO-123, SUP-45, etc.)
3. **Qualification**: Filter for alert-worthy contexts
4. **Prioritization**: Assign P1/P2/P3 priority
5. **Context Builder**: Generate human-readable alerts

## Key Concepts

### Signals vs Alerts

- **Signal**: Raw monitoring data (e.g., "Weather alert in Chennai")
- **Alert**: Human-facing notification (e.g., "Weather Disruption Risk detected")

### Confidence Scores

- 0.0-1.0 scale
- Used in qualification rules (>= 0.85 is high confidence)
- Used in priority assignment

### Priority Levels

- **P1**: High urgency (act immediately)
- **P2**: Medium urgency (act within hours)
- **P3**: Low urgency (act within days)

### Alert Priority Rules

**P1 Triggers**:
- CRITICAL severity + confidence >= 0.75
- HIGH severity + confidence >= 0.85
- Impact within 6 hours + confidence >= 0.80

**P2 Triggers**:
- HIGH severity + confidence >= 0.70
- MEDIUM severity + confidence >= 0.85
- Impact within 6 hours + confidence >= 0.70

**P3**: Everything else

### Qualification Rules

An alert is generated if:
- ✅ One high-confidence signal (>= 0.85), OR
- ✅ Two or more medium-confidence signals (>= 0.75 each)

Otherwise:
- ❌ Single low-confidence signal (< 0.70) is rejected

## Testing

```bash
cd /workspaces/firefly2/backend
python app/services/alerts/test_pipeline.py
```

You should see:
- 5 input signals
- 4 risk contexts after grouping
- 2 alerts after qualification
- Priority assignments (P1, P2)

## Mock Data Signals

The pipeline includes 5 mock signals:

1. **Weather Disruption** (Chennai)
   - Severity: HIGH
   - Confidence: 0.92
   - Impact: 6 hours

2. **PO Delay Risk** (PO-123 #1)
   - Severity: MEDIUM
   - Confidence: 0.85
   - Impact: 2 days

3. **Supplier Performance** (SUP-45)
   - Severity: MEDIUM
   - Confidence: 0.78
   - Impact: 1 week

4. **News Risk** (Southeast Asia)
   - Severity: LOW
   - Confidence: 0.62
   - Impact: 3 days

5. **PO Delay Risk** (PO-123 #2)
   - Severity: HIGH
   - Confidence: 0.88
   - Impact: 3 days

## Example Alert Output

```json
{
  "alertId": "ALERT-ABC123",
  "title": "⚠️ Delivery Delay Risk - Purchase Order PO-123",
  "summary": "Alert Summary:\n• 🟡 Supplier port delays detected...\n• 🟠 Updated: Supplier forecast shows 2-3 day delay...\n\nThis affects the procurement for PO-123.\n\nRecommendation: Review related orders and consider contingency plans.",
  "priority": "P2",
  "confidenceScore": 0.865,
  "relatedSignals": ["PO_DELAY_RISK"],
  "createdAt": "2025-01-22T10:30:00"
}
```

## File Structure

```
backend/app/services/alerts/
├── __init__.py              # Main exports
├── schemas.py               # Data models (MonitoringSignal, Alert, etc.)
├── mock_data.py             # Test signals
├── pipeline.py              # Orchestration logic
├── api.py                   # FastAPI endpoints
├── test_pipeline.py         # Test runner
├── ingestion/               # Signal validation (5 modules)
├── aggregation/             # Grouping by entity
├── qualification/           # Alert qualification rules
├── prioritization/          # Priority assignment
└── context_builder/         # Human-readable formatting
```

## Design Principles

✅ **Layered**: Each stage has one job
✅ **Transparent**: No black boxes, all rules are explicit
✅ **Enterprise-Safe**: No DB writes, no notifications, no financial calculations
✅ **MVP-Ready**: Uses mock data, works standalone
✅ **Extensible**: Easy to add new signal types or change rules
✅ **Testable**: Each layer can be unit tested
✅ **Documented**: Clear code comments and examples

## Next Steps

1. **Test it**: Run `test_pipeline.py` to verify everything works
2. **Integrate it**: Add the alerts router to your main FastAPI app
3. **Customize it**: Modify mock data or qualification rules as needed
4. **Extend it**: Add real data sources when monitoring agents are ready

## Common Modifications

### Change Qualification Rules
Edit: `qualification/alert_filter.py`
- Modify confidence thresholds
- Change signal count requirements
- Add new conditions

### Change Priority Logic
Edit: `prioritization/urgency_ranker.py`
- Adjust severity-based rules
- Change confidence weights
- Modify impact window parsing

### Add New Signal Type
1. Add enum to `schemas.py` (SignalType, SourceType)
2. Create ingestion module (e.g., `ingestion/custom_ingest.py`)
3. Update `pipeline.py` to call new ingestion module
4. Add test data in `mock_data.py`

### Customize Alert Titles/Summaries
Edit: `context_builder/alert_explainer.py`
- Modify `generate_title()` function
- Modify `generate_summary()` function
- Change emoji mappings

## Constraints (As Designed)

⚠️ **Does NOT**:
- Write to database
- Send notifications
- Calculate financial impact
- Use LLMs
- Integrate with real monitoring yet

These are intentional MVP constraints. Add them in future versions as needed.

## Questions?

Refer to: `ALERTS_MODULE_IMPLEMENTATION.md` for comprehensive documentation.
