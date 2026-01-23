"""
Quick test script for the Alerts Module JSONL pipeline.

Run this to test the alerts module without needing FastAPI server.
"""

import sys
import json
from pathlib import Path

# Add backend to path (go up one level from tests folder)
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "app" / "services"))

from alerts.pipeline import run_alerts_pipeline_from_jsonl


def main():
    """Test the JSONL-based alerts pipeline."""
    print("=" * 70)
    print("Testing Alerts Module JSONL Pipeline")
    print("=" * 70)
    
    # Run pipeline from JSONL files
    print("\n[Test] Running alerts pipeline from JSONL files...\n")
    alerts = run_alerts_pipeline_from_jsonl()
    
    # Display results
    print("\n" + "=" * 70)
    print(f"Generated {len(alerts)} alerts")
    print("=" * 70)
    
    if alerts:
        for i, alert in enumerate(alerts, 1):
            print(f"\n📢 Alert #{i}:")
            print(f"  ID: {alert.alertId}")
            print(f"  Title: {alert.title}")
            print(f"  Priority: {alert.priority}")
            print(f"  Confidence: {alert.confidenceScore:.0%}")
            print(f"  Related Signals: {[s.value for s in alert.relatedSignals]}")
            print(f"  Summary:\n{alert.summary}")
            print("-" * 70)
        
        # Output as JSON for verification
        print("\n[Test] JSON Output:")
        print(json.dumps([a.model_dump(mode='json') for a in alerts], indent=2))
    else:
        print("\n⚠️  No alerts generated (check JSONL files exist and contain valid signals)")
    
    print("\n✅ Test complete!")
    return len(alerts) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
