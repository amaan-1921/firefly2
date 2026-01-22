"""
Alerts Module Implementation Guide

This document provides a complete overview of the Alerts Module architecture,
implementation, and usage.
"""

# Alerts Module - Complete Implementation

## Overview

The Alerts Module is a multi-layered system that transforms raw monitoring signals 
from various agents into actionable, human-readable alerts with appropriate urgency levels.

### Design Philosophy
- **Layered Architecture**: Each layer has a single responsibility
- **Clear Logic**: No LLMs or complex heuristics - rules are explicit and auditable
- **Enterprise-Safe**: No financial calculations, no database writes, no notifications
- **MVP-Ready**: Uses mock data for testing without external dependencies

---

## Architecture

```
Input: MonitoringSignal objects (from weather, news, PO, supplier agents)
         ↓
    ┌────────────────────────────────────────────┐
    │ INGESTION LAYER                            │
    │ Validate & normalize signals by source     │
    └────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────┐
    │ AGGREGATION LAYER                          │
    │ Group signals by entity (PO, supplier)     │
    │ Output: RiskContext objects                │
    └────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────┐
    │ QUALIFICATION LAYER                        │
    │ Filter: Only alert-worthy contexts         │
    │ Rules: High confidence OR multiple signals │
    └────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────┐
    │ PRIORITIZATION LAYER                       │
    │ Rank by urgency (P1, P2, P3)               │
    │ Consider severity, confidence, impact time │
    └────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────┐
    │ CONTEXT BUILDER LAYER                      │
    │ Convert to human-readable Alert objects    │
    │ Generate clear explanations                │
    └────────────────────────────────────────────┘
         ↓
Output: Alert objects (human-facing alerts)
```

---

## Core Data Models (schemas.py)

### MonitoringSignal
Raw signal from a monitoring agent.

```python
MonitoringSignal(
    signalType: SignalType,              # WEATHER_DISRUPTION, PO_DELAY_RISK, etc.
    sourceType: SourceType,              # WEATHER_AGENT, NEWS_AGENT, etc.
    sourceReference: str,                # PO-123, SUP-45, REGION-CHENNAI
    severityLevel: SeverityLevel,        # LOW, MEDIUM, HIGH, CRITICAL
    confidenceScore: float,              # 0.0 to 1.0
    expectedImpactWindow: str,           # "2 hours", "1 day", "3 days"
    evidence: str,                       # Brief explanation
    timestamp: datetime                  # When signal was generated
)
```

### RiskContext
Groups related signals by a common entity.

```python
RiskContext(
    contextId: str,                      # Unique ID: RISK-XXXXX
    relatedEntity: str,                  # PO-123, SUP-45, REGION-CHENNAI
    signals: List[MonitoringSignal],     # All signals for this entity
    createdAt: datetime
)
```

### Alert
Human-facing alert derived from one or more signals.

```python
Alert(
    alertId: str,                        # Unique ID: ALERT-XXXXX
    title: str,                          # Concise title with emoji
    summary: str,                        # Detailed explanation
    priority: AlertPriority,             # P1 (High), P2 (Medium), P3 (Low)
    confidenceScore: float,              # Average confidence (0.0 to 1.0)
    relatedSignals: List[SignalType],    # Types of signals involved
    createdAt: datetime
)
```

---

## Layer Details

### 1. Ingestion Layer (ingestion/)

**Purpose**: Validate and normalize signals from each source type

**Modules**:
- `weather_ingest.py`: Weather signals
- `news_ingest.py`: News/external risk signals
- `po_delay_ingest.py`: PO delay signals
- `supplier_ingest.py`: Supplier performance signals

**Logic**:
- Filter signals by source and type
- Validate confidence scores (0.0-1.0)
- Validate reference formats (PO-XXX, SUP-XXX)
- Reject invalid signals
- Return normalized signals

**Output**: List of validated MonitoringSignal objects

---

### 2. Aggregation Layer (aggregation/signal_grouper.py)

**Purpose**: Group signals by related entity

**Logic**:
- Extract `sourceReference` from each signal
- Group all signals with the same reference
- Create a RiskContext for each group

**Example**:
```
Input signals:
  - PO-123, WEATHER_DISRUPTION (severity=HIGH, confidence=0.92)
  - PO-123, PO_DELAY_RISK (severity=MEDIUM, confidence=0.85)
  - PO-123, PO_DELAY_RISK (severity=HIGH, confidence=0.88)

Output RiskContext:
  - contextId: RISK-XYZ123
  - relatedEntity: PO-123
  - signals: [all 3 signals above]
```

**Output**: List of RiskContext objects

---

### 3. Qualification Layer (qualification/alert_filter.py)

**Purpose**: Decide which RiskContexts should become alerts

**Qualification Rules** (MVP):
1. **Reject**: Single low-confidence signal (confidence < 0.7)
2. **Alert**: One high-confidence signal (confidence >= 0.85)
3. **Alert**: Two or more medium-confidence signals (confidence >= 0.75 each)

**Logic**:
```
For each RiskContext:
  - Count high-confidence signals (>= 0.85)
  - Count medium-confidence signals (>= 0.75)
  
  if high_confidence_count >= 1:
      QUALIFY for alert
  elif medium_confidence_count >= 2:
      QUALIFY for alert
  else:
      REJECT (not alert-worthy)
```

**Output**: Filtered list of RiskContext objects that qualify for alerts

---

### 4. Prioritization Layer (prioritization/urgency_ranker.py)

**Purpose**: Assign priority levels (P1, P2, P3) based on urgency

**Priority Assignment**:

**P1 (High Urgency)**:
- CRITICAL severity + confidence >= 0.75, OR
- HIGH severity + confidence >= 0.85, OR
- Urgent impact window (within 6 hours) + confidence >= 0.80

**P2 (Medium Urgency)**:
- HIGH severity + confidence >= 0.70, OR
- MEDIUM severity + confidence >= 0.85, OR
- Urgent impact window (within 6 hours) + confidence >= 0.70

**P3 (Low Urgency)**:
- Everything else

**Impact Window Parsing**:
- "2 hours" → Urgent (within 6 hours)
- "1 day" → Not urgent
- "1 week" → Not urgent
- "30 minutes" → Urgent

**Output**: List of (RiskContext, AlertPriority) tuples, sorted by priority

---

### 5. Context Builder Layer (context_builder/alert_explainer.py)

**Purpose**: Convert RiskContexts into human-readable Alert objects

**Title Generation**:
- Extract entity type from reference (PO-123 → Purchase Order)
- Collect signal types
- If single signal type: "⚠️ [Risk Type] - [Entity]"
- If multiple signal types: "⚠️ Multiple Risks Detected - [Entity]"

**Summary Generation**:
- Combine evidence from all signals
- Add severity emoji (🔴🟠🟡🟢)
- Include impact window
- Add entity context (e.g., "This affects the procurement for PO-123")
- Include recommendation: "Review related orders and consider contingency plans"

**Example Summary**:
```
Alert Summary:
🟠 Supplier port delays detected. Expected delivery is at risk due to 
port congestion in Chennai. (Impact window: 2 days)
🟠 Updated: Supplier forecast shows 2-3 day delay due to weather 
impact on production facility in Chennai. (Impact window: 3 days)

This affects the procurement for PO-123.

Recommendation: Review related orders and consider contingency plans.
```

**Output**: List of Alert objects ready for presentation

---

## Pipeline Orchestration (pipeline.py)

**Main Function**: `run_alerts_pipeline(signals=None) -> List[Alert]`

**Flow**:
1. Load mock signals (if none provided)
2. Run Ingestion layer
3. Run Aggregation layer
4. Run Qualification layer
5. Run Prioritization layer
6. Run Context Builder layer
7. Return final alerts

**Example Usage**:
```python
from app.services.alerts import run_alerts_pipeline

alerts = run_alerts_pipeline()  # Uses mock data
for alert in alerts:
    print(f"Priority: {alert.priority}")
    print(f"Title: {alert.title}")
```

---

## API Endpoints (api.py)

### GET /alerts/run-mock

Execute the complete alerts pipeline using mock data.

**Response**:
```json
[
  {
    "alertId": "ALERT-ABC123",
    "title": "⚠️ Weather Disruption Risk - Region: CHENNAI",
    "summary": "Alert Summary:\n🟠 Severe thunderstorm warning...",
    "priority": "P1",
    "confidenceScore": 0.92,
    "relatedSignals": ["WEATHER_DISRUPTION"],
    "createdAt": "2025-01-22T10:30:00"
  }
]
```

**Usage**:
```bash
curl http://localhost:8000/alerts/run-mock
```

---

## Mock Data (mock_data.py)

The `get_mock_signals()` function generates 5 realistic test signals:

1. **WEATHER_DISRUPTION** in Chennai (HIGH severity, 0.92 confidence)
2. **PO_DELAY_RISK** for PO-123 (MEDIUM severity, 0.85 confidence)
3. **SUPPLIER_PERFORMANCE_DROP** for SUP-45 (MEDIUM severity, 0.78 confidence)
4. **NEWS_RISK** about Southeast Asia strikes (LOW severity, 0.62 confidence)
5. **PO_DELAY_RISK** update for PO-123 (HIGH severity, 0.88 confidence)

**Pipeline Result with Mock Data**:
- Input: 5 signals
- After Ingestion: 5 valid signals
- After Aggregation: 4 risk contexts (grouped by entity)
- After Qualification: 2 contexts qualify
- After Prioritization: 2 alerts (1 P1, 1 P2)

---

## Testing

### Run Pipeline Test
```bash
cd /workspaces/firefly2/backend
python app/services/alerts/test_pipeline.py
```

### Expected Output
```
ALERTS MODULE PIPELINE TEST
================================================================================
[Pipeline] Loaded 5 signals
[Pipeline] Starting Ingestion layer...
[Pipeline] Ingestion complete: 5 valid signals
[Pipeline] Starting Aggregation layer...
[Pipeline] Aggregation complete: 4 risk contexts created
[Pipeline] Starting Qualification layer...
[Pipeline] Qualification complete: 2 contexts qualify for alerts
[Pipeline] Starting Prioritization layer...
[Pipeline] Prioritization complete: contexts ranked by priority
[Pipeline] Starting Context Builder layer...
[Pipeline] Context Builder complete: 2 alerts created
[Pipeline] ✅ Pipeline execution completed successfully

RESULTS: Generated 2 alerts
================================================================================
```

---

## Integration with FastAPI

To integrate with your main FastAPI application:

```python
from fastapi import FastAPI
from app.services.alerts.api import router as alerts_router

app = FastAPI()

# Include alerts router
app.include_router(alerts_router)

# Now available at: GET /alerts/run-mock
```

---

## Key Design Decisions

### 1. No Database Writes
- Alerts are computed in-memory
- No persistence layer
- Each pipeline run is independent

### 2. No LLM Integration
- All explanations are template-based
- Deterministic and auditable
- Fast execution

### 3. No Financial Calculations
- Prioritization based on urgency, not impact
- Enables simple, explainable rules

### 4. Source-Specific Ingestion
- Each source has its own module
- Easy to add new sources
- Clear validation per source type

### 5. Entity-Based Aggregation
- Signals grouped by what they affect (PO, supplier, region)
- Makes context clear to users
- Natural alignment with business processes

### 6. Simple Qualification Rules
- No machine learning
- Clear thresholds
- Easy to explain to stakeholders

### 7. Transparent Prioritization
- Rules based on severity, confidence, timing
- No hidden weights or algorithms
- Auditable decision logic

### 8. Human-Readable Context
- Plain language explanations
- Emoji for quick visual reference
- Non-technical user audience

---

## Future Enhancements (Out of Scope for MVP)

1. **Real Data Integration**
   - Connect to actual monitoring agents
   - Remove mock data usage

2. **Database Persistence**
   - Store alerts for historical tracking
   - Enable alert acknowledgment/resolution

3. **Notifications**
   - Email alerts for P1
   - Slack/Teams integration
   - SMS for critical alerts

4. **Financial Impact**
   - Estimate cost of delays
   - Reorder recommendations
   - Risk-weighted prioritization

5. **User Preferences**
   - Alert thresholds per user/team
   - Subscription to specific signal types
   - Alert aggregation options

6. **Advanced Analytics**
   - Alert patterns over time
   - False positive tracking
   - Effectiveness metrics

7. **Integration with Resolution**
   - Link alerts to mitigation actions
   - Track resolution status
   - Feedback loop for rule refinement

---

## Code Structure

```
backend/app/services/alerts/
├── __init__.py                    # Module exports
├── schemas.py                     # Pydantic models
├── mock_data.py                   # Test data
├── pipeline.py                    # Orchestration
├── api.py                         # FastAPI endpoints
├── test_pipeline.py               # Test script
│
├── ingestion/
│   ├── __init__.py
│   ├── weather_ingest.py
│   ├── news_ingest.py
│   ├── po_delay_ingest.py
│   └── supplier_ingest.py
│
├── aggregation/
│   ├── __init__.py
│   └── signal_grouper.py
│
├── qualification/
│   ├── __init__.py
│   └── alert_filter.py
│
├── prioritization/
│   ├── __init__.py
│   └── urgency_ranker.py
│
└── context_builder/
    ├── __init__.py
    └── alert_explainer.py
```

---

## Summary

The Alerts Module provides:
✅ Clean, layered architecture
✅ Transparent, auditable logic
✅ Human-readable alerts
✅ Enterprise-safe (no DB, no notifications)
✅ MVP-ready with mock data
✅ Easy to extend and modify
✅ Well-documented code

Each layer is independent and can be tested/modified separately.
The pipeline is orchestrated clearly with minimal dependencies.
