# Alerts Configuration - Quick Reference

## Quick Start

```python
from app.services.alerts.config import (
    qualification_config,
    prioritization_config,
    get_config_summary,
    update_qualification_threshold,
    update_p1_threshold
)

# View current config
print(get_config_summary())

# Update thresholds
update_qualification_threshold(0.8)  # Validated update
update_p1_threshold(0.9)

# Or direct modification
qualification_config.single_signal_confidence_threshold = 0.8
prioritization_config.p1_high_severity_min_confidence = 0.9
```

---

## Configuration Parameters

### Qualification (Signal Filtering)
| Parameter | Default | Use Case |
|---|---|---|
| `single_signal_confidence_threshold` | 0.7 | Minimum confidence for single signals to qualify |

**Higher (0.8-0.9)** → Fewer alerts (stricter filtering)  
**Lower (0.5-0.6)** → More alerts (looser filtering)

---

### Prioritization (P1/P2/P3 Assignment)
| Parameter | Default | Use Case |
|---|---|---|
| `p1_critical_severity_min_confidence` | 0.0 | CRITICAL severity always P1 |
| `p1_high_severity_min_confidence` | 0.85 | HIGH severity threshold for P1 |
| `p1_immediate_impact_enabled` | True | Include time urgency in P1 |
| `p2_high_severity_min_confidence` | 0.5 | HIGH severity threshold for P2 |
| `p2_medium_severity_max_confidence` | 1.0 | MEDIUM severity threshold for P2 |

**Higher P1 threshold** → Fewer P1 alerts (stricter)  
**Lower P1 threshold** → More P1 alerts (looser)  
**Higher P2 threshold** → Fewer P2 alerts, more P3  
**Lower P2 threshold** → More P2 alerts, fewer P3

---

### Ingestion (JSONL Loading)
| Parameter | Default | Use Case |
|---|---|---|
| `default_weather_file` | "app/services/monitoring/weather_risk/weather_output.jsonl" | Weather signal file |
| `default_news_file` | "app/services/monitoring/news_intelligence/agent_test/scraped_articles.jsonl" | News article file |
| `log_parse_errors` | True | Print warnings for parse errors |
| `skip_invalid_records` | True | Continue on parse errors vs. raise |

---

## Common Scenarios

### ❌ Too Many Alerts?
```python
update_qualification_threshold(0.8)  # Stricter filtering
```

### ❌ Too Many P1 Alerts?
```python
prioritization_config.p1_high_severity_min_confidence = 0.9
```

### ❌ Missing Important Alerts?
```python
update_qualification_threshold(0.5)  # Looser filtering
```

### ❌ Want to Ignore Time Urgency?
```python
prioritization_config.p1_immediate_impact_enabled = False
```

---

## Pipeline Impact

```
Configuration → Ingestion → Qualification → Prioritization → Context Builder
     ↓                ↓              ↓             ↓               ↓
ingestion_config     Load        Confidence   P1/P2/P3      Alert text
                    JSONL       threshold   assignment    formatting
```

Each layer independently uses its configuration, so changes cascade through.

---

## Files

- **Config Definition:** `backend/app/services/alerts/config.py`
- **Usage Guide:** `backend/app/services/alerts/CONFIG_USAGE.md`
- **Test Suite:** `tests/test_config.py`
- **Implementation Details:** `CONFIGURATION_IMPLEMENTATION.md`

---

## Helper Functions

```python
# Get current configuration as dict
summary = get_config_summary()

# Validate and update qualification threshold
update_qualification_threshold(0.75)  # 0.0-1.0

# Validate and update P1 threshold
update_p1_threshold(0.85)  # 0.0-1.0
```

---

## Testing Configuration

```bash
cd /mnt/OldVolume/internship/firefly2
/venv/bin/python tests/test_config.py
```

Shows how different configuration values affect alert generation.

---

## Default Behavior (No Changes)

```
Qualification:    Single signals need 0.7+ confidence
Prioritization:   P1 = HIGH severity + 0.85+ confidence
                  P2 = HIGH severity + 0.5+ confidence
                  P3 = Everything else
Ingestion:        Load from app/services/.../weather_output.jsonl
                  and app/services/.../scraped_articles.jsonl
```

✅ **Safe to experiment** - Restore original values anytime.
