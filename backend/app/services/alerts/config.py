"""
Alerts module configuration.

Centralized configuration for all thresholds, file paths, and alert generation parameters.
Allows fine-tuning of alert behavior without modifying core logic.
"""

from dataclasses import dataclass


@dataclass
class QualificationConfig:
    """
    Qualification layer thresholds.
    
    Controls which RiskContexts should become alerts based on confidence and signal count.
    """
    # Minimum confidence score for single-signal contexts to qualify for alert
    # Single signals below this threshold are filtered out
    single_signal_confidence_threshold: float = 0.7
    
    # Multiple signals with any confidence qualify for alerts
    # (correlation from different sources indicates legitimate risk)
    multi_signal_confidence_threshold: float = 0.0


@dataclass
class PrioritizationConfig:
    """
    Prioritization layer thresholds.
    
    Controls priority assignment logic (P1, P2, P3).
    """
    # P1 (High) priority thresholds
    p1_critical_severity_min_confidence: float = 0.0  # CRITICAL severity always P1
    p1_high_severity_min_confidence: float = 0.85     # HIGH severity needs 0.85+
    p1_immediate_impact_enabled: bool = True          # Immediate impact = P1
    
    # P2 (Medium) priority thresholds
    p2_high_severity_min_confidence: float = 0.5      # HIGH severity with 0.5-0.85 = P2
    p2_medium_severity_max_confidence: float = 1.0    # MEDIUM severity with high confidence = P2
    
    # Default: Everything else is P3


@dataclass
class ContextBuilderConfig:
    """
    Context builder (alert explanation) configuration.
    
    Controls how alerts are explained and presented to users.
    """
    # Entity type labels
    entity_labels = {
        "PO": "Purchase Order",
        "SUPPLIER": "Supplier",
        "REGION": "Region",
        "NEWS": "News",
    }
    
    # Signal type descriptions
    signal_descriptions = {
        "WEATHER_DISRUPTION": "Weather Disruption Risk",
        "PO_DELAY_RISK": "Delivery Delay Risk",
        "SUPPLIER_PERFORMANCE_DROP": "Supplier Performance Concern",
        "NEWS_RISK": "Supply Chain News Alert",
    }
    
    # Context messages by entity type
    context_messages = {
        "PO": "This affects the procurement for {entity}.",
        "SUPPLIER": "This affects {entity} and related orders.",
        "REGION": "This affects the {region_name} region.",
        "NEWS": "This is relevant news information affecting supply chain.",
        "WEATHER": "This weather risk affects the {location} location.",
    }
    
    # Recommendations by entity type
    recommendations = {
        "PO": "Review related purchase orders and consider expedited alternatives.",
        "SUPPLIER": "Review supplier performance and consider backup suppliers.",
        "REGION": "Review shipments in this region and consider route alternatives.",
        "NEWS": "Review the details and assess impact on ongoing operations.",
        "WEATHER": "Monitor conditions and prepare contingency logistics plans.",
    }


@dataclass
class IngestionConfig:
    """
    Ingestion layer file paths and parsing configuration.
    
    Supports both default paths and custom overrides.
    """
    # Default JSONL file paths (relative to backend directory)
    default_weather_file: str = "app/services/monitoring/weather_risk/weather_output.jsonl"
    default_news_file: str = "app/services/monitoring/news_intelligence/agent_test/scraped_articles.jsonl"
    
    # Whether to log warnings for unparseable records
    log_parse_errors: bool = True
    
    # Whether to skip records with missing required fields
    skip_invalid_records: bool = True


# Global configuration instances
qualification_config = QualificationConfig()
prioritization_config = PrioritizationConfig()
context_builder_config = ContextBuilderConfig()
ingestion_config = IngestionConfig()


def update_qualification_threshold(single_signal_threshold: float) -> None:
    """
    Update the single-signal confidence threshold.
    
    Args:
        single_signal_threshold: New threshold (0.0 to 1.0)
    """
    if not 0.0 <= single_signal_threshold <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")
    qualification_config.single_signal_confidence_threshold = single_signal_threshold


def update_p1_threshold(high_severity_confidence: float) -> None:
    """
    Update the P1 priority threshold for HIGH severity signals.
    
    Args:
        high_severity_confidence: New minimum confidence for HIGH severity → P1 (0.0 to 1.0)
    """
    if not 0.0 <= high_severity_confidence <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")
    prioritization_config.p1_high_severity_min_confidence = high_severity_confidence


def update_p2_threshold(high_severity_confidence: float) -> None:
    """
    Update the P2 priority threshold for HIGH severity signals.
    
    Args:
        high_severity_confidence: New minimum confidence for HIGH severity → P2 (0.0 to 1.0)
    """
    if not 0.0 <= high_severity_confidence <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")
    prioritization_config.p2_high_severity_min_confidence = high_severity_confidence


def get_config_summary() -> dict:
    """
    Get a summary of all current configuration values.
    
    Returns:
        Dictionary with all configuration values
    """
    return {
        "qualification": {
            "single_signal_threshold": qualification_config.single_signal_confidence_threshold,
            "multi_signal_threshold": qualification_config.multi_signal_confidence_threshold,
        },
        "prioritization": {
            "p1_critical_severity_min_confidence": prioritization_config.p1_critical_severity_min_confidence,
            "p1_high_severity_min_confidence": prioritization_config.p1_high_severity_min_confidence,
            "p1_immediate_impact_enabled": prioritization_config.p1_immediate_impact_enabled,
            "p2_high_severity_min_confidence": prioritization_config.p2_high_severity_min_confidence,
            "p2_medium_severity_max_confidence": prioritization_config.p2_medium_severity_max_confidence,
        },
        "ingestion": {
            "default_weather_file": ingestion_config.default_weather_file,
            "default_news_file": ingestion_config.default_news_file,
            "log_parse_errors": ingestion_config.log_parse_errors,
            "skip_invalid_records": ingestion_config.skip_invalid_records,
        },
    }
