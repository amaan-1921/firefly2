"""
Weather signal ingestion module.

Handles validation and normalization of weather-related signals from JSONL files.
"""

from typing import List, Optional
from ..schemas import MonitoringSignal, SourceType, SignalType
from .jsonl_loader import load_jsonl_file
from ..config import ingestion_config


def ingest_weather_signals(
    file_path: Optional[str] = None
) -> List[MonitoringSignal]:
    """
    Ingest and normalize weather signals from JSONL file.
    
    Args:
        file_path: Path to weather signals JSONL file.
                  If None, uses default path: 
                  backend/app/services/monitoring/weather_risk/weather_output.jsonl
        
    Returns:
        List of validated and normalized MonitoringSignal objects.
        Returns empty list if file not found or contains no valid signals.
    """
    # Use default path if not provided
    if file_path is None:
        file_path = ingestion_config.default_weather_file
    
    # Load raw JSON records from file
    raw_records = load_jsonl_file(file_path)
    
    normalized = []
    
    for record in raw_records:
        try:
            # Normalize the record to match MonitoringSignal schema
            normalized_record = normalize_weather_signal(record)
            
            # Parse as MonitoringSignal (with flexible schema)
            signal = MonitoringSignal(**normalized_record)
            normalized.append(signal)
            
        except Exception as e:
            if ingestion_config.log_parse_errors:
                print(f"[Weather Ingestion] Warning: Failed to parse weather signal: {e}")
            if not ingestion_config.skip_invalid_records:
                raise
            continue
    
    print(f"[Weather Ingestion] Processed {len(normalized)} valid weather signals")
    return normalized


def normalize_weather_signal(record: dict) -> dict:
    """
    Normalize a raw weather signal record to MonitoringSignal schema.
    
    Ensures required fields exist and handles variations from real data.
    
    Args:
        record: Raw record from JSONL file
        
    Returns:
        Normalized record ready for MonitoringSignal parsing
    """
    normalized = {}
    
    # signalType - should be WEATHER_DISRUPTION
    normalized['signalType'] = record.get('signalType', 'WEATHER_DISRUPTION')
    
    # sourceType - real weather data uses "External", normalize to WEATHER_AGENT
    source_type = record.get('sourceType', 'External')
    normalized['sourceType'] = source_type  # Will be normalized by Pydantic validator
    
    # sourceReference - location name
    normalized['sourceReference'] = record.get('sourceReference', 'Unknown')
    
    # severityLevel - normalize from string to enum
    severity = record.get('severityLevel', 'MEDIUM')
    normalized['severityLevel'] = severity  # Will be normalized by Pydantic validator
    
    # confidenceScore - should be float 0-1
    confidence = record.get('confidenceScore', 0.7)
    try:
        normalized['confidenceScore'] = float(confidence)
    except (ValueError, TypeError):
        normalized['confidenceScore'] = 0.7
    
    # expectedImpactWindow - string describing time window
    normalized['expectedImpactWindow'] = record.get(
        'expectedImpactWindow', 
        '1–3 days'
    )
    
    # evidence - human-readable explanation
    normalized['evidence'] = record.get('evidence', 'Weather signal detected')
    
    # timestamp - ISO datetime string (optional)
    if 'timestamp' in record:
        normalized['timestamp'] = record['timestamp']
    
    return normalized
