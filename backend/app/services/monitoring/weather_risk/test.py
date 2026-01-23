"""Test script for Weather Risk Agent."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agent import WeatherRiskAgent
from schemas import MonitoringSignal

# Load environment variables from .env file
load_dotenv()


async def test_weather_risk_agent():
    """
    Test the Weather Risk Agent with mock or real API key.
    """
    # Get API key from environment variable
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        print("ERROR: OPENWEATHER_API_KEY environment variable not set")
        print("Please set your OpenWeatherMap API key:")
        print("  export OPENWEATHER_API_KEY='your_api_key_here'")
        return False
    
    print("=" * 60)
    print("Testing Weather Risk Agent")
    print("=" * 60)
    
    try:
        # Initialize the agent
        agent = WeatherRiskAgent(api_key=api_key)
        print(f"\n✓ Agent initialized successfully")
        print(f"  Monitoring {len(agent.locations)} locations:")
        for loc in agent.locations:
            print(f"    - {loc.name} ({loc.latitude}, {loc.longitude})")
        
        # Evaluate weather conditions
        print(f"\n→ Fetching weather data and evaluating risks...")
        signals = await agent.evaluate()
        
        # Display results
        print(f"\n✓ Evaluation complete")
        print(f"  Total signals detected: {len(signals)}")
        
        # Show raw weather data for each location
        print(f"\n{'=' * 60}")
        print("RAW OPENWEATHERMAP API RESPONSES:")
        print("=" * 60)
        for location in agent.locations:
            raw_data = await agent.client.fetch_weather_data(location)
            if raw_data:
                print(f"\n{location.name}:")
                print(json.dumps(raw_data, indent=2))
            else:
                print(f"\n{location.name}: Failed to fetch data")
        
        if signals:
            print(f"\n{'=' * 60}")
            print("DETECTED WEATHER RISKS:")
            print("=" * 60)
            
            for i, signal in enumerate(signals, 1):
                print(f"\nSignal #{i}:")
                print(f"  Location: {signal.sourceReference}")
                print(f"  Severity: {signal.severityLevel}")
                print(f"  Confidence: {signal.confidenceScore}")
                print(f"  Evidence: {signal.evidence}")
                print(f"  Impact Window: {signal.expectedImpactWindow}")
                print(f"  Timestamp: {signal.timestamp}")
                
                # Verify all required fields
                assert signal.signalType == "WEATHER_DISRUPTION"
                assert signal.sourceType == "External"
                assert isinstance(signal, MonitoringSignal)
            
            # Append signals to JSONL file
            jsonl_filename = "weather_output.jsonl"
            with open(jsonl_filename, 'a') as f:
                for signal in signals:
                    # Convert signal to dict and write as JSON line
                    signal_dict = signal.model_dump(mode='json')
                    f.write(json.dumps(signal_dict) + '\n')
            
            print(f"\n{'=' * 60}")
            print("✓ All signals validated successfully!")
            print(f"✓ Signals appended to: {jsonl_filename}")
            print("=" * 60)
        else:
            print("\n✓ No severe weather risks detected")
        
        return True
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Test Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the async test
    success = asyncio.run(test_weather_risk_agent())
    
    if success:
        print("\n✓ Weather Risk Agent is working correctly!")
        exit(0)
    else:
        print("\n✗ Weather Risk Agent test failed!")
        exit(1)
