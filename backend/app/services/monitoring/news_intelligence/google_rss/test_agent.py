import sys
import os
import json
import logging
from datetime import datetime
from agent import run

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create output directory
os.makedirs("test_output", exist_ok=True)

# Test context
test_context = {
    "orchestrator_id": "test-orchestrator",
    "job_id": "test-job-001",
    "timestamp": datetime.utcnow().isoformat()
}

# Run the agent
result = run(test_context)

# Print result
print("\n=== Agent Result ===")
print(json.dumps(result, indent=2))

# If successful, read and display the output file
if result["success"] and "output_file" in result:
    with open(result["output_file"], "r") as f:
        lines = f.readlines()
    
    print(f"\n=== Output File Contents (JSONL format) ===")
    
    # First line is metadata
    if lines:
        metadata = json.loads(lines[0])
        print(f"Signals Count: {metadata.get('signals_count', 'N/A')}")
        print(f"Signals in this run: {metadata.get('signals_in_this_run', 'N/A')}")
    
    # Print first signal (second line)
    if len(lines) > 1:
        first_signal = json.loads(lines[1])
        print(f"\nFirst Signal:")
        print(json.dumps(first_signal, indent=2))