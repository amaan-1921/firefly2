# Alerts Configuration System Implementation

## Overview

A centralized configuration system has been added to the alerts module to allow fine-tuning of thresholds and behavior without modifying core code.

## New Files Created

1. **[app/services/alerts/config.py](../backend/app/services/alerts/config.py)** (164 lines)
   - Central configuration dataclasses and helper functions
   - Four configuration categories:
     - `QualificationConfig` - Signal filtering thresholds
     - `PrioritizationConfig` - Priority assignment logic
     - `ContextBuilderConfig` - Alert presentation templates
     - `IngestionConfig` - JSONL file paths and error handling

2. **[CONFIG_USAGE.md](../backend/app/services/alerts/CONFIG_USAGE.md)** (Complete guide)
   - Detailed documentation for each configuration option
   - Common configuration scenarios and solutions
   - Helper functions reference
   - Configuration hierarchy and default values table

3. **[tests/test_config.py](../tests/test_config.py)** (Test suite)
   - Demonstrates how configuration affects alert generation
   - 5 test cases showing different configuration scenarios

## Updated Modules

All modules now import and use configuration values instead of hardcoded thresholds:

### 1. **qualification/alert_filter.py**
- Imports `qualification_config`
- Uses `qualification_config.single_signal_confidence_threshold` instead of hardcoded `0.7`
- Updated docstring to mention configuration

### 2. **prioritization/urgency_ranker.py**
- Imports `prioritization_config`
- Uses configurable thresholds for P1/P2/P3 assignment:
  - `p1_critical_severity_min_confidence`
  - `p1_high_severity_min_confidence`
  - `p1_immediate_impact_enabled`
  - `p2_high_severity_min_confidence`
  - `p2_medium_severity_max_confidence`

### 3. **ingestion/weather_ingest.py**
- Imports `ingestion_config`
- Uses `ingestion_config.default_weather_file` instead of hardcoded path
- Uses `ingestion_config.log_parse_errors` to control warning output
- Uses `ingestion_config.skip_invalid_records` for error handling behavior

### 4. **ingestion/news_ingest.py**
- Imports `ingestion_config`
- Uses `ingestion_config.default_news_file` instead of hardcoded path
- Uses `ingestion_config.log_parse_errors` for error logging
- Uses `ingestion_config.skip_invalid_records` for error handling

### 5. **ingestion/po_delay_ingest.py**
- Added `ingestion_config` import for consistency

### 6. **ingestion/supplier_ingest.py**
- Added `ingestion_config` import for consistency

## Configuration Categories

### QualificationConfig
Controls which signals become alerts in the Qualification layer.

```python
single_signal_confidence_threshold: float = 0.7      # Minimum confidence for single signals
multi_signal_confidence_threshold: float = 0.0       # Minimum for multiple signals (always qualify)
```

**Impact:** Signals below threshold are filtered out before reaching Prioritization.

---

### PrioritizationConfig
Controls priority assignment logic (P1, P2, P3) in the Prioritization layer.

```python
# P1 (High) thresholds
p1_critical_severity_min_confidence: float = 0.0     # CRITICAL always P1
p1_high_severity_min_confidence: float = 0.85        # HIGH + 0.85+ = P1
p1_immediate_impact_enabled: bool = True             # Immediate impact = P1

# P2 (Medium) thresholds
p2_high_severity_min_confidence: float = 0.5         # HIGH + 0.5+ = P2
p2_medium_severity_max_confidence: float = 1.0       # MEDIUM + 1.0+ = P2
```

**Impact:** Changes how priority is assigned to alerts.

---

### ContextBuilderConfig
Controls how alerts are formatted and presented to users.

```python
entity_labels: dict                    # How to label PO/Supplier/Region/News
signal_descriptions: dict              # Risk type descriptions
context_messages: dict                 # Explanation templates by entity type
recommendations: dict                  # Action recommendations by entity type
```

**Impact:** Customizes the text of alert titles, summaries, and recommendations.

---

### IngestionConfig
Controls how signals are loaded from JSONL files.

```python
default_weather_file: str = "app/..."        # Weather signal file path
default_news_file: str = "app/..."           # News article file path
log_parse_errors: bool = True                # Print warnings for parse failures
skip_invalid_records: bool = True            # Continue on errors vs. raise exception
```

**Impact:** Determines where to load signals from and how to handle parse errors.

---

## Usage Examples

### Example 1: Update at Runtime
```python
from app.services.alerts.config import qualification_config, update_qualification_threshold

# Option 1: Direct modification
qualification_config.single_signal_confidence_threshold = 0.8

# Option 2: Validated helper function
update_qualification_threshold(0.75)  # Validates 0.0 <= value <= 1.0
```

### Example 2: Configure at Startup
```python
# main.py
from fastapi import FastAPI
from app.services.alerts.config import prioritization_config

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Configure for stricter P1 alerts
    prioritization_config.p1_high_severity_min_confidence = 0.95
    print("Alerts configured for strict P1 filtering")
```

### Example 3: Test Different Configurations
```python
# test_config.py
from app.services.alerts.config import qualification_config
from app.services.alerts.pipeline import run_alerts_pipeline

def test_loose_qualification():
    original = qualification_config.single_signal_confidence_threshold
    try:
        qualification_config.single_signal_confidence_threshold = 0.5
        alerts = run_alerts_pipeline()
        assert len(alerts) > 10  # Expect more alerts
    finally:
        qualification_config.single_signal_confidence_threshold = original
```

### Example 4: Get Config Summary
```python
from app.services.alerts.config import get_config_summary

summary = get_config_summary()
print(summary)
# {
#   'qualification': {'single_signal_threshold': 0.7, ...},
#   'prioritization': {'p1_high_severity_min_confidence': 0.85, ...},
#   'ingestion': {'default_weather_file': 'app/...', ...}
# }
```

---

## Common Configuration Adjustments

| Scenario | Adjustment | Rationale |
|---|---|---|
| Too many false alerts | Increase `single_signal_confidence_threshold` to 0.8+ | Filter out low-confidence noise |
| Missing critical alerts | Decrease `single_signal_confidence_threshold` to 0.6 | Catch more potential issues |
| Too many P1 alerts | Increase `p1_high_severity_min_confidence` to 0.9+ | Make P1 more selective |
| Not enough P1 alerts | Decrease `p1_high_severity_min_confidence` to 0.75 | Catch more high-priority cases |
| Don't care about timing | Set `p1_immediate_impact_enabled = False` | Ignore impact window urgency |
| Custom alert text | Update `context_builder_config` labels/messages | Customize wording |

---

## Configuration Flow Through Pipeline

```
Input Signals
    ↓
Ingestion (uses ingestion_config.default_weather_file, default_news_file)
    ↓
Aggregation (no config)
    ↓
Qualification (uses qualification_config.single_signal_confidence_threshold)
    → Signals below threshold are filtered out
    ↓
Prioritization (uses prioritization_config P1/P2/P3 thresholds)
    → Priority assigned based on severity/confidence/urgency
    ↓
Context Builder (uses context_builder_config labels/messages/recommendations)
    → Alert text formatted and customized
    ↓
Final Alert JSON
```

---

## Testing the Configuration

Run the test suite to see configuration effects:

```bash
cd /mnt/OldVolume/internship/firefly2
/venv/bin/python tests/test_config.py
```

This runs 5 tests:
1. **Default Configuration** - Baseline alert count
2. **Strict Qualification** - Threshold 0.8 (fewer alerts)
3. **Strict P1 Priority** - Threshold 0.95 (fewer P1 alerts)
4. **Loose P2 Priority** - Threshold 0.3 (more P2 alerts)
5. **Helper Functions** - Validation and update functions

---

## Key Benefits

✅ **No Code Changes Needed** - Adjust thresholds without modifying source code
✅ **Runtime Configuration** - Change settings while application is running
✅ **Validated Updates** - Helper functions validate input ranges
✅ **Centralized Control** - All settings in one place, easy to find
✅ **Environment-Specific** - Configure differently for dev/staging/production
✅ **Testable** - Easy to test different scenarios
✅ **Backward Compatible** - All updates are backwards compatible

---

## Configuration Reference

See [CONFIG_USAGE.md](../backend/app/services/alerts/CONFIG_USAGE.md) for:
- Detailed parameter descriptions
- Common configuration scenarios
- Configuration helper functions
- Default values reference table
- Testing examples
