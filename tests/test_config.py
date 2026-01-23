"""
Test script demonstrating alert configuration usage.

Shows how to modify thresholds and observe their effects on alert generation.
"""

from app.services.alerts.config import (
    qualification_config,
    prioritization_config,
    ingestion_config,
    get_config_summary,
    update_qualification_threshold,
    update_p1_threshold
)
from app.services.alerts.pipeline import run_alerts_pipeline


def test_default_configuration():
    """Test with default configuration values."""
    print("\n" + "="*70)
    print("TEST 1: Default Configuration")
    print("="*70)
    
    summary = get_config_summary()
    print("\nCurrent Configuration:")
    print(f"  Qualification threshold: {summary['qualification']['single_signal_threshold']}")
    print(f"  P1 HIGH severity minimum: {summary['prioritization']['p1_high_severity_min_confidence']}")
    print(f"  P2 HIGH severity minimum: {summary['prioritization']['p2_high_severity_min_confidence']}")
    
    alerts = run_alerts_pipeline()
    
    p1_count = len([a for a in alerts if a.priority.value == 'P1'])
    p2_count = len([a for a in alerts if a.priority.value == 'P2'])
    p3_count = len([a for a in alerts if a.priority.value == 'P3'])
    
    print(f"\nResults:")
    print(f"  Total alerts: {len(alerts)}")
    print(f"  P1 alerts: {p1_count}")
    print(f"  P2 alerts: {p2_count}")
    print(f"  P3 alerts: {p3_count}")


def test_strict_qualification():
    """Test with stricter qualification threshold."""
    print("\n" + "="*70)
    print("TEST 2: Stricter Qualification (threshold = 0.8)")
    print("="*70)
    
    original_threshold = qualification_config.single_signal_confidence_threshold
    
    try:
        qualification_config.single_signal_confidence_threshold = 0.8
        print(f"\nUpdated qualification threshold to 0.8")
        print("Expected: Fewer alerts (low-confidence signals filtered out)")
        
        alerts = run_alerts_pipeline()
        
        p1_count = len([a for a in alerts if a.priority.value == 'P1'])
        p2_count = len([a for a in alerts if a.priority.value == 'P2'])
        p3_count = len([a for a in alerts if a.priority.value == 'P3'])
        
        print(f"\nResults:")
        print(f"  Total alerts: {len(alerts)}")
        print(f"  P1 alerts: {p1_count}")
        print(f"  P2 alerts: {p2_count}")
        print(f"  P3 alerts: {p3_count}")
        
    finally:
        # Restore original
        qualification_config.single_signal_confidence_threshold = original_threshold


def test_strict_p1_priority():
    """Test with stricter P1 priority assignment."""
    print("\n" + "="*70)
    print("TEST 3: Stricter P1 Priority (HIGH severity requires 0.95 confidence)")
    print("="*70)
    
    original_threshold = prioritization_config.p1_high_severity_min_confidence
    
    try:
        prioritization_config.p1_high_severity_min_confidence = 0.95
        print(f"\nUpdated P1 HIGH severity threshold to 0.95")
        print("Expected: Fewer P1 alerts, more P2/P3")
        
        alerts = run_alerts_pipeline()
        
        p1_count = len([a for a in alerts if a.priority.value == 'P1'])
        p2_count = len([a for a in alerts if a.priority.value == 'P2'])
        p3_count = len([a for a in alerts if a.priority.value == 'P3'])
        
        print(f"\nResults:")
        print(f"  Total alerts: {len(alerts)}")
        print(f"  P1 alerts: {p1_count}")
        print(f"  P2 alerts: {p2_count}")
        print(f"  P3 alerts: {p3_count}")
        
    finally:
        # Restore original
        prioritization_config.p1_high_severity_min_confidence = original_threshold


def test_loose_p2_priority():
    """Test with looser P2 priority assignment."""
    print("\n" + "="*70)
    print("TEST 4: Looser P2 Priority (HIGH severity requires 0.3 confidence)")
    print("="*70)
    
    original_threshold = prioritization_config.p2_high_severity_min_confidence
    
    try:
        prioritization_config.p2_high_severity_min_confidence = 0.3
        print(f"\nUpdated P2 HIGH severity threshold to 0.3")
        print("Expected: More P2 alerts, fewer P3")
        
        alerts = run_alerts_pipeline()
        
        p1_count = len([a for a in alerts if a.priority.value == 'P1'])
        p2_count = len([a for a in alerts if a.priority.value == 'P2'])
        p3_count = len([a for a in alerts if a.priority.value == 'P3'])
        
        print(f"\nResults:")
        print(f"  Total alerts: {len(alerts)}")
        print(f"  P1 alerts: {p1_count}")
        print(f"  P2 alerts: {p2_count}")
        print(f"  P3 alerts: {p3_count}")
        
    finally:
        # Restore original
        prioritization_config.p2_high_severity_min_confidence = original_threshold


def test_helper_functions():
    """Test configuration helper functions."""
    print("\n" + "="*70)
    print("TEST 5: Configuration Helper Functions")
    print("="*70)
    
    original_qual = qualification_config.single_signal_confidence_threshold
    original_p1 = prioritization_config.p1_high_severity_min_confidence
    
    try:
        print("\nUsing update_qualification_threshold(0.75)...")
        update_qualification_threshold(0.75)
        print(f"  Updated to: {qualification_config.single_signal_confidence_threshold}")
        
        print("\nUsing update_p1_threshold(0.9)...")
        update_p1_threshold(0.9)
        print(f"  Updated to: {prioritization_config.p1_high_severity_min_confidence}")
        
        print("\nTesting validation (should fail)...")
        try:
            update_qualification_threshold(1.5)
            print("  ❌ ERROR: Should have raised ValueError!")
        except ValueError as e:
            print(f"  ✅ Correctly rejected: {e}")
            
    finally:
        # Restore originals
        qualification_config.single_signal_confidence_threshold = original_qual
        prioritization_config.p1_high_severity_min_confidence = original_p1


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ALERTS MODULE CONFIGURATION TEST SUITE")
    print("="*70)
    
    test_default_configuration()
    test_strict_qualification()
    test_strict_p1_priority()
    test_loose_p2_priority()
    test_helper_functions()
    
    print("\n" + "="*70)
    print("✅ All configuration tests complete!")
    print("="*70)
