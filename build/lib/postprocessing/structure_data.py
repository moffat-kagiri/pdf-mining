from typing import List, Dict, Any
import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

def structure_table(layout_elements: List[Any]) -> pd.DataFrame:
    """
    Convert detected layout elements into structured tabular format.
    
    Args:
        layout_elements: List of layout elements from LayoutParser
        
    Returns:
        pandas.DataFrame containing structured data with columns for
        element type, text content, confidence score, and coordinates
    """
    try:
        structured_data = []
        
        for element in layout_elements:
            data = {
                'type': element.type,
                'text': element.text if hasattr(element, 'text') else '',
                'confidence': float(element.score) if hasattr(element, 'score') else 0.0,
                'x1': element.coordinates[0],
                'y1': element.coordinates[1],
                'x2': element.coordinates[2],
                'y2': element.coordinates[3],
                'page_number': getattr(element, 'page_number', 1)
            }
            structured_data.append(data)
            
        df = pd.DataFrame(structured_data)
        
        # Sort by vertical position (top to bottom)
        df = df.sort_values('y1')
        
        # Add derived columns
        df['area'] = (df['x2'] - df['x1']) * (df['y2'] - df['y1'])
        df['height'] = df['y2'] - df['y1']
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to structure layout data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error