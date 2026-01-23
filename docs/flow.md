1. INGESTION Layer
Files: ingestion/*.py

What it does:

Reads JSONL files (weather signals, news articles)
Normalizes different source formats into standardized MonitoringSignal objects
Validates data using Pydantic schemas
Key modules:

weather_ingest.py - Loads weather JSONL, maps fields to MonitoringSignal
news_ingest.py - Converts news articles to signals (relevance_score → confidenceScore)
jsonl_loader.py - Handles JSONL file reading
po_delay_ingest.py, supplier_ingest.py - Mock data sources (no JSONL yet)
Output: List of MonitoringSignal objects

2. AGGREGATION Layer
File: signal_grouper.py

What it does:

Groups signals by common entity (PO ID, supplier ID, region)
Creates RiskContext objects that bundle related signals
Example: 3 weather signals for "Mumbai" + 2 news articles about "Mumbai" → 1 RiskContext
Logic:


Group signals by sourceReference (entity)For each group → create RiskContext(signals=[...])
Output: List of RiskContext objects

3. QUALIFICATION Layer
File: alert_filter.py

What it does:

Decides which RiskContexts should become alerts (filtering rules)
Prevents low-quality, unreliable signals from generating alerts
Rules:

✅ Alert if: Multiple signals in same context (any confidence)
✅ Alert if: Single signal with confidence ≥ 0.7
❌ Skip: Single signal with confidence < 0.7
Output: Filtered list of RiskContext objects

4. PRIORITIZATION Layer
File: urgency_ranker.py

What it does:

Assigns priority levels (P1, P2, P3) based on severity & confidence
Sorts alerts by urgency
Priority Logic:

P1 (High): CRITICAL severity + high confidence, OR HIGH severity + confidence ≥0.85, OR immediate impact window
P2 (Medium): HIGH severity with medium confidence, OR MEDIUM severity with high confidence
P3 (Low): MEDIUM severity with medium confidence, OR LOW severity
Output: List of (RiskContext, AlertPriority) tuples, sorted P1→P2→P3

5. CONTEXT BUILDER Layer
File: alert_explainer.py

What it does:

Converts RiskContext + Priority into human-readable Alert objects
Generates alert title, summary, and evidence description
No LLM - uses template-based text generation
Functions:

generate_title() - Creates title like "Weather Risk in Mumbai"
generate_summary() - Builds explanation from signals (evidence, impact window, confidence)
get_severity_emoji() - Deprecated (was returning emojis, now empty)
Output: List of Alert JSON objects

