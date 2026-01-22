"""README for Weather Risk Agent Tests."""

# Weather Risk Agent Tests

This directory contains two test files for the Weather Risk Agent:

## test.py - Real API Test

Tests the Weather Risk Agent with real OpenWeatherMap API data.

**Requirements:**
- Valid OpenWeatherMap API key set in `OPENWEATHER_API_KEY` environment variable

**Usage:**
```bash
export OPENWEATHER_API_KEY='your_api_key_here'
python test.py
```

**What it tests:**
- Agent initialization
- Real API data fetching for Chennai and Mumbai
- Weather risk evaluation logic
- Signal validation (MonitoringSignal schema)

## test_mock.py - Mock Test (Recommended for Development)

Tests the Weather Risk Agent with mocked API responses. No API key required!

**Usage:**
```bash
python test_mock.py
```

**What it tests:**
- High severity weather alert detection (cyclone warning)
- Threshold-based risk detection (rainfall > 50mm)
- Empty signal list for safe conditions
- Signal validation and schema compliance

## Expected Output

Both tests will display:
- ✓ Successful initialization
- ✓ Number of signals detected
- ✓ Details of each detected risk (location, severity, confidence, evidence)
- ✓ Validation results

## Quick Start

For quick validation without an API key:
```bash
python test_mock.py
```

For production testing with real data:
```bash
export OPENWEATHER_API_KEY='your_key'
python test.py
```
