"""
JSONL file loader utility for safely reading monitoring signals.

Handles:
- Missing files (returns empty list instead of error)
- Malformed JSON lines (skips with warning)
- Safe parsing without strict validation
"""

import json
import os
from typing import List, Dict, Any


def load_jsonl_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a JSONL file and return list of parsed JSON objects.
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        List of dictionaries parsed from JSON lines.
        Returns empty list if file doesn't exist or is empty.
        Skips malformed lines and logs warnings.
    """
    if not os.path.exists(file_path):
        print(f"[JSONL Loader] File not found: {file_path}")
        return []
    
    records = []
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"[JSONL Loader] Warning: Malformed JSON at line {line_num} of {file_path}: {e}")
                    continue
        
        print(f"[JSONL Loader] Successfully loaded {len(records)} records from {file_path}")
        return records
        
    except IOError as e:
        print(f"[JSONL Loader] Error reading file {file_path}: {e}")
        return []
