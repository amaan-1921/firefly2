"""
Pipeline orchestration module.

Orchestrates the complete alerts pipeline:
Ingestion → Aggregation → Qualification → Prioritization → Context Builder

This module coordinates all layers to transform raw monitoring signals
into human-facing alerts.

Supports both:
- Mock data mode (for testing): run_alerts_pipeline()
- JSONL file mode (for production): run_alerts_pipeline_from_jsonl()
"""

from typing import List, Optional
from .schemas import Alert, MonitoringSignal
from .mock_data import get_mock_signals
from .ingestion.weather_ingest import ingest_weather_signals
from .ingestion.news_ingest import ingest_news_signals
from .ingestion.po_delay_ingest import ingest_po_delay_signals
from .ingestion.supplier_ingest import ingest_supplier_signals
from .aggregation.signal_grouper import group_signals_by_entity
from .qualification.alert_filter import filter_qualifying_contexts
from .prioritization.urgency_ranker import rank_by_urgency
from .context_builder.alert_explainer import build_alerts


def run_alerts_pipeline(signals: List[MonitoringSignal] = None) -> List[Alert]:
    """
    Execute the complete alerts pipeline with mock data.
    
    Pipeline stages:
    1. Ingestion: Validate and normalize signals from each source
    2. Aggregation: Group signals by entity (PO, supplier, region)
    3. Qualification: Filter to signals that should become alerts
    4. Prioritization: Rank by urgency and assign priority levels
    5. Context Builder: Convert to human-readable alerts
    
    Args:
        signals: List of MonitoringSignal objects. If None, uses mock data.
        
    Returns:
        List of Alert objects ready for presentation
    """
    # Step 1: Load signals (use mock data if not provided)
    if signals is None:
        signals = get_mock_signals()
    
    print(f"[Pipeline] Loaded {len(signals)} signals")
    
    # Step 2: Ingestion - Validate and normalize by source type
    print("[Pipeline] Starting Ingestion layer...")
    # For mock data mode, pass None to ingestion functions so they filter mock signals
    weather_signals = ingest_weather_signals(None)
    news_signals = ingest_news_signals(None)
    po_signals = ingest_po_delay_signals(None)
    supplier_signals = ingest_supplier_signals(None)
    
    # Combine all ingested signals
    ingested_signals = weather_signals + news_signals + po_signals + supplier_signals
    print(f"[Pipeline] Ingestion complete: {len(ingested_signals)} valid signals")
    
    # Step 3: Aggregation - Group by entity
    print("[Pipeline] Starting Aggregation layer...")
    risk_contexts = group_signals_by_entity(ingested_signals)
    print(f"[Pipeline] Aggregation complete: {len(risk_contexts)} risk contexts created")
    
    # Step 4: Qualification - Filter for alert-worthy contexts
    print("[Pipeline] Starting Qualification layer...")
    qualifying_contexts = filter_qualifying_contexts(risk_contexts)
    print(f"[Pipeline] Qualification complete: {len(qualifying_contexts)} contexts qualify for alerts")
    
    # Step 5: Prioritization - Rank by urgency
    print("[Pipeline] Starting Prioritization layer...")
    ranked_contexts = rank_by_urgency(qualifying_contexts)
    print(f"[Pipeline] Prioritization complete: contexts ranked by priority")
    
    # Step 6: Context Builder - Convert to alerts
    print("[Pipeline] Starting Context Builder layer...")
    final_alerts = build_alerts(ranked_contexts)
    print(f"[Pipeline] Context Builder complete: {len(final_alerts)} alerts created")
    
    print("[Pipeline] ✅ Pipeline execution completed successfully")
    
    return final_alerts


def run_alerts_pipeline_from_jsonl(
    weather_file_path: Optional[str] = None,
    news_file_path: Optional[str] = None
) -> List[Alert]:
    """
    Execute the complete alerts pipeline reading from JSONL files.
    
    Loads monitoring signals from JSONL files (weather and news)
    and runs the full alerts pipeline to generate alerts.
    
    Handles missing or empty files gracefully - returns alerts
    from whatever signals are available.
    
    Pipeline stages:
    1. Ingestion: Load and normalize signals from JSONL files
    2. Aggregation: Group signals by entity
    3. Qualification: Filter to alert-worthy contexts
    4. Prioritization: Rank by urgency
    5. Context Builder: Convert to human-readable alerts
    
    Args:
        weather_file_path: Path to weather signals JSONL.
                          Defaults to backend/app/services/monitoring/weather_risk/weather_output.jsonl
        news_file_path: Path to news articles JSONL.
                       Defaults to backend/app/services/monitoring/news_intelligence/agent_test/scraped_articles.jsonl
        
    Returns:
        List of Alert objects ready for presentation
    """
    print("[Pipeline] Starting alerts pipeline from JSONL files...")
    
    # Step 1: Ingestion - Load signals from JSONL files
    print("[Pipeline] Starting Ingestion layer...")
    weather_signals = ingest_weather_signals(weather_file_path)
    news_signals = ingest_news_signals(news_file_path)
    
    # Note: Not ingesting PO/supplier signals as they don't have JSONL sources yet
    ingested_signals = weather_signals + news_signals
    print(f"[Pipeline] Ingestion complete: {len(ingested_signals)} valid signals")
    
    if not ingested_signals:
        print("[Pipeline] ⚠️ No signals loaded from JSONL files")
        return []
    
    # Step 2: Aggregation - Group by entity
    print("[Pipeline] Starting Aggregation layer...")
    risk_contexts = group_signals_by_entity(ingested_signals)
    print(f"[Pipeline] Aggregation complete: {len(risk_contexts)} risk contexts created")
    
    # Step 3: Qualification - Filter for alert-worthy contexts
    print("[Pipeline] Starting Qualification layer...")
    qualifying_contexts = filter_qualifying_contexts(risk_contexts)
    print(f"[Pipeline] Qualification complete: {len(qualifying_contexts)} contexts qualify for alerts")
    
    if not qualifying_contexts:
        print("[Pipeline] ℹ️ No signals qualified for alerts")
        return []
    
    # Step 4: Prioritization - Rank by urgency
    print("[Pipeline] Starting Prioritization layer...")
    ranked_contexts = rank_by_urgency(qualifying_contexts)
    print(f"[Pipeline] Prioritization complete: contexts ranked by priority")
    
    # Step 5: Context Builder - Convert to alerts
    print("[Pipeline] Starting Context Builder layer...")
    final_alerts = build_alerts(ranked_contexts)
    print(f"[Pipeline] Context Builder complete: {len(final_alerts)} alerts created")
    
    print("[Pipeline] ✅ Pipeline execution completed successfully")
    
    return final_alerts
