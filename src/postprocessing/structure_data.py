# src/postprocessing/structure_data.py
import pandas as pd
from typing import List, Dict

def structure_table(elements):
    structured = []
    for element in elements:
        # Skip non-dict elements
        if not isinstance(element, dict):
            continue
            
        structured.append({
            'type': element.get('type', 'unknown'),
            'content': element.get('text', ''),
            'bbox': element.get('bbox', []),
            'source': element.get('source', 'unknown')
        })
    return pd.DataFrame(structured)

# Explicit exports
__all__ = ['structure_table']