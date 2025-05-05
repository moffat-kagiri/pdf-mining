# src/postprocessing/structure_data.py
import pandas as pd
from typing import List, Dict

def structure_table(layout_elements: List[Dict]) -> pd.DataFrame:
    """
    Convert layout elements to structured DataFrame
    Args:
        layout_elements: List of dicts from layout analysis
    Returns:
        pd.DataFrame: Structured table with columns ['type', 'content', 'bbox']
    """
    structured_data = []
    
    for element in layout_elements:
        structured_data.append({
            'type': element.get('type', 'unknown'),
            'content': element.get('text', '') or element.get('content', ''),
            'bbox': element.get('bbox', []),
            'source': element.get('source', 'unknown')
        })
    
    return pd.DataFrame(structured_data)

# Explicit exports
__all__ = ['structure_table']