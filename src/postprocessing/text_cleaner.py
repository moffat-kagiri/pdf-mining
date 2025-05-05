import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Clean extracted text by removing noise and normalizing."""
    if not text:
        return ""
    
    # Basic text cleaning
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # normalize whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove non-ASCII
    return text

def process_pymupdf_output(layout: Dict[str, Any]) -> List[Dict[str, str]]:
    """Process text blocks from PyMuPDF layout."""
    results = []
    if not layout:
        return results
        
    for block in layout.get('blocks', []):
        text = clean_text(block.get('text', ''))
        if text:
            results.append({
                'text': text,
                'type': block.get('type', 'unknown'),
                'bbox': block.get('bbox', []),
                'confidence': block.get('confidence', 1.0)
            })
    return results

def process_donut_output(image, predictions) -> List[Dict[str, str]]:
    """Process text predictions from Donut model."""
    results = []
    if not predictions:
        return results
        
    for pred in predictions:
        text = clean_text(pred.get('text', ''))
        if text:
            results.append({
                'text': text,
                'type': pred.get('label', 'text'),
                'bbox': pred.get('box', []),
                'confidence': pred.get('score', 0.0)
            })
    return results