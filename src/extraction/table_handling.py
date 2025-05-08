import re
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def detect_tables(text: str) -> List[List[List[str]]]:
    """Identify and extract tabular data from text"""
    tables = []
    
    # Split into potential tables
    table_candidates = re.split(r'\n{2,}', text.strip())
    
    for candidate in table_candidates:
        if is_likely_table(candidate):
            table = parse_table(candidate)
            if table:
                tables.append(table)
    
    return tables

def is_likely_table(text: str) -> bool:
    """Heuristics for table detection"""
    lines = text.split('\n')
    if len(lines) < 3:
        return False
    
    # Check for consistent delimiters
    delimiter_counts = {}
    for line in lines[:5]:  # Check first few lines
        for delim in ['|', ',', '\t']:
            delimiter_counts[delim] = delimiter_counts.get(delim, 0) + line.count(delim)
    
    # If any delimiter appears consistently
    if any(count > len(lines) * 2 for count in delimiter_counts.values()):
        return True
    
    # Check for aligned columns
    if len({len(line.split()) for line in lines[:5]}) == 1:
        return True
    
    return False

def parse_table(text: str) -> Optional[List[List[str]]]:
    """Convert table-like text to 2D array"""
    try:
        lines = text.split('\n')
        
        # Determine delimiter
        first_line = lines[0]
        delim = max(['|', ',', '\t'], 
                   key=lambda d: first_line.count(d))
        
        return [re.split(fr'{delim}+', line.strip()) for line in lines]
    
    except Exception as e:
        logger.warning(f"Table parsing failed: {str(e)}")
        return None