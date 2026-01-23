"""
Test script for the Alerts Module.

Validates that the complete pipeline works with mock data.
Can be run to verify the alerts module implementation.
"""

import sys
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.services.alerts import run_alerts_pipeline


def test_alerts_pipeline():
    """Test the complete alerts pipeline with mock data."""
    print("=" * 80)
    print("ALERTS MODULE PIPELINE TEST")
    print("=" * 80)
    print()
    
    try:
        alerts = run_alerts_pipeline()
        
        print()
        print("=" * 80)
        print(f"RESULTS: Generated {len(alerts)} alerts")
        print("=" * 80)
        print()
        
        for i, alert in enumerate(alerts, 1):
            print(f"Alert #{i}")
            print(f"  ID: {alert.alertId}")
            print(f"  Title: {alert.title}")
            print(f"  Priority: {alert.priority}")
            print(f"  Confidence: {alert.confidenceScore:.0%}")
            print(f"  Signal Types: {', '.join(str(s.value) for s in alert.relatedSignals)}")
            print(f"  Summary:")
            for line in alert.summary.split('\n'):
                print(f"    {line}")
            print()
        
        print("=" * 80)
        print("✅ PIPELINE TEST PASSED")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ PIPELINE TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_alerts_pipeline()
    sys.exit(0 if success else 1)
