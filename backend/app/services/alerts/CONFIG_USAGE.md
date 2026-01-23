# Alerts Configuration Guide

The alerts module now uses a centralized configuration system for easy control of thresholds and behavior without modifying core code.

## Configuration Overview

Configuration is split into four main categories:

### 1. **Qualification Config** - Signal Filtering
Controls which signals become alerts.

```python
from app.services.alerts.config import qualification_config

# Default: Single signals need confidence >= 0.7
qualification_config.single_signal_confidence_threshold = 0.7

# Multiple signals always qualify (confidence >= 0.0)
qualification_config.multi_signal_confidence_threshold = 0.0
```

**Use Cases:**
- Increase to 0.8 if too many low-confidence alerts
- Decrease to 0.5 if missing important signals
- Single signals < threshold are filtered out in Qualification layer

---

### 2. **Prioritization Config** - Alert Severity
Controls P1/P2/P3 priority assignment logic.

```python
from app.services.alerts.config import prioritization_config

# P1 (High Priority) thresholds
prioritization_config.p1_critical_severity_min_confidence = 0.0     # CRITICAL always P1
prioritization_config.p1_high_severity_min_confidence = 0.85        # HIGH + 0.85+ confidence = P1
prioritization_config.p1_immediate_impact_enabled = True            # Immediate impact = P1

# P2 (Medium Priority) thresholds
prioritization_config.p2_high_severity_min_confidence = 0.5         # HIGH + 0.5+ confidence = P2
prioritization_config.p2_medium_severity_max_confidence = 1.0       # MEDIUM + any confidence = P2
```

**Priority Assignment Logic:**
```
P1 (High):
  - CRITICAL severity (any confidence >= 0.0), OR
  - HIGH severity + confidence >= 0.85, OR
  - Immediate impact window (if enabled) + confidence >= 0.80

P2 (Medium):
  - HIGH severity + confidence >= 0.50 (if not P1), OR
  - MEDIUM severity + confidence >= 1.0, OR
  - Urgent window + confidence >= 0.70

P3 (Low):
  - Everything else (default)
```

**Use Cases:**
- Increase `p1_high_severity_min_confidence` to 0.9 for stricter P1 alerts
- Decrease to 0.75 for more P1 alerts
- Disable `p1_immediate_impact_enabled` to ignore time urgency

---

### 3. **Context Builder Config** - Alert Presentation
Controls how alerts are formatted and explained to users.

```python
from app.services.alerts.config import context_builder_config

# Entity type labels (how to describe POs, suppliers, regions, etc.)
context_builder_config.entity_labels = {
    "PO": "Purchase Order",
    "SUPPLIER": "Supplier",
    "REGION": "Region",
    "NEWS": "News",
}

# Signal type descriptions (risk names)
context_builder_config.signal_descriptions = {
    "WEATHER_DISRUPTION": "Weather Disruption Risk",
    "PO_DELAY_RISK": "Delivery Delay Risk",
    "SUPPLIER_PERFORMANCE_DROP": "Supplier Performance Concern",
    "NEWS_RISK": "Supply Chain News Alert",
}

# Context messages (customizable explanation templates)
context_builder_config.context_messages = {
    "PO": "This affects the procurement for {entity}.",
    "SUPPLIER": "This affects {entity} and related orders.",
    "REGION": "This affects the {region_name} region.",
    "NEWS": "This is relevant news information affecting supply chain.",
    "WEATHER": "This weather risk affects the {location} location.",
}

# Recommendations (customizable action items)
context_builder_config.recommendations = {
    "PO": "Review related purchase orders and consider expedited alternatives.",
    "SUPPLIER": "Review supplier performance and consider backup suppliers.",
    "REGION": "Review shipments in this region and consider route alternatives.",
    "NEWS": "Review the details and assess impact on ongoing operations.",
    "WEATHER": "Monitor conditions and prepare contingency logistics plans.",
}
```

---

### 4. **Ingestion Config** - Data Loading
Controls how signals are loaded from JSONL files.

```python
from app.services.alerts.config import ingestion_config

# Default file paths (can be overridden per function call)
ingestion_config.default_weather_file = "app/services/monitoring/weather_risk/weather_output.jsonl"
ingestion_config.default_news_file = "app/services/monitoring/news_intelligence/agent_test/scraped_articles.jsonl"

# Error handling behavior
ingestion_config.log_parse_errors = True          # Print warnings for bad records
ingestion_config.skip_invalid_records = True      # Continue if record fails to parse
```

---

## Common Configuration Scenarios

### Scenario 1: Too Many False Alerts
**Problem:** Getting too many low-confidence alerts

**Solution:**
```python
from app.services.alerts.config import qualification_config, prioritization_config

# Increase qualification threshold
qualification_config.single_signal_confidence_threshold = 0.8

# Increase P2 threshold to make fewer P1 alerts
prioritization_config.p2_high_severity_min_confidence = 0.6
```

### Scenario 2: Missing Critical Alerts
**Problem:** Important alerts are being filtered out

**Solution:**
```python
from app.services.alerts.config import qualification_config

# Decrease threshold to catch more signals
qualification_config.single_signal_confidence_threshold = 0.6
```

### Scenario 3: Wrong Priority Distribution
**Problem:** Too many P1 alerts, need to be more selective

**Solution:**
```python
from app.services.alerts.config import prioritization_config

# Make P1 stricter - require higher confidence for HIGH severity signals
prioritization_config.p1_high_severity_min_confidence = 0.9

# Make P2 threshold higher too
prioritization_config.p2_high_severity_min_confidence = 0.7
```

### Scenario 4: Ignore Time Urgency
**Problem:** Don't want to prioritize based on impact window

**Solution:**
```python
from app.services.alerts.config import prioritization_config

# Disable immediate impact urgency
prioritization_config.p1_immediate_impact_enabled = False
```

---

## Configuration Helper Functions

### Get Current Configuration
```python
from app.services.alerts.config import get_config_summary

summary = get_config_summary()
print(summary)
# Output:
# {
#   'qualification': {...},
#   'prioritization': {...},
#   'ingestion': {...}
# }
```

### Update Thresholds with Validation
```python
from app.services.alerts.config import update_qualification_threshold, update_p1_threshold

# Validates input is between 0.0 and 1.0
update_qualification_threshold(0.75)
update_p1_threshold(0.9)
```

---

## Configuration at Startup

To set configuration when your application starts:

```python
# main.py
from fastapi import FastAPI
from app.services.alerts.config import (
    qualification_config,
    prioritization_config,
    update_qualification_threshold,
    update_p1_threshold
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Configure alerts based on environment/deployment
    update_qualification_threshold(0.75)
    update_p1_threshold(0.9)
    
    # Or directly:
    qualification_config.single_signal_confidence_threshold = 0.75
    prioritization_config.p1_high_severity_min_confidence = 0.9
    
    print("Alerts module configured for stricter filtering")
```

---

## Testing Configuration Changes

```python
# test_config.py
from app.services.alerts.config import (
    qualification_config,
    prioritization_config,
    get_config_summary
)
from app.services.alerts.pipeline import run_alerts_pipeline

def test_with_loose_qualification():
    """Test with lower confidence threshold"""
    original = qualification_config.single_signal_confidence_threshold
    
    try:
        qualification_config.single_signal_confidence_threshold = 0.5
        
        alerts = run_alerts_pipeline()
        assert len(alerts) > 10  # Expect more alerts
        
    finally:
        # Restore original
        qualification_config.single_signal_confidence_threshold = original

def test_with_strict_p1():
    """Test with stricter P1 priority"""
    original = prioritization_config.p1_high_severity_min_confidence
    
    try:
        prioritization_config.p1_high_severity_min_confidence = 0.95
        
        alerts = run_alerts_pipeline()
        p1_count = len([a for a in alerts if a.priority.value == 'P1'])
        assert p1_count < 5  # Expect fewer P1 alerts
        
    finally:
        prioritization_config.p1_high_severity_min_confidence = original
```

---

## Configuration Hierarchy

The pipeline uses configuration in this order:

```
Ingestion (loads from JSONL)
    ↓ [uses ingestion_config for file paths]
Qualification (filters by confidence)
    ↓ [uses qualification_config threshold]
Prioritization (assigns P1/P2/P3)
    ↓ [uses prioritization_config thresholds]
Context Builder (formats alert text)
    ↓ [uses context_builder_config labels/messages]
Final Alert JSON
```

Each layer independently uses its configuration, so changes propagate through the pipeline.

---

## Default Values Reference

| Parameter | Default | Range | Purpose |
|---|---|---|---|
| `single_signal_confidence_threshold` | 0.7 | 0.0-1.0 | Minimum confidence for single signals to qualify |
| `p1_critical_severity_min_confidence` | 0.0 | 0.0-1.0 | CRITICAL severity always P1 |
| `p1_high_severity_min_confidence` | 0.85 | 0.0-1.0 | HIGH severity threshold for P1 |
| `p1_immediate_impact_enabled` | True | True/False | Include time urgency in P1 logic |
| `p2_high_severity_min_confidence` | 0.5 | 0.0-1.0 | HIGH severity threshold for P2 |
| `p2_medium_severity_max_confidence` | 1.0 | 0.0-1.0 | MEDIUM severity threshold for P2 |
| `log_parse_errors` | True | True/False | Print parse error warnings |
| `skip_invalid_records` | True | True/False | Continue on parse errors vs. raise exception |
