"""
Pipeline orchestration module.

Orchestrates the complete alerts pipeline:
Ingestion → Aggregation → Qualification → Prioritization → Context Builder

This module coordinates all layers to transform raw monitoring signals
into human-facing alerts.
"""

from typing import List
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
    Execute the complete alerts pipeline.
    
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
    weather_signals = ingest_weather_signals(signals)
    news_signals = ingest_news_signals(signals)
    po_signals = ingest_po_delay_signals(signals)
    supplier_signals = ingest_supplier_signals(signals)
    
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
