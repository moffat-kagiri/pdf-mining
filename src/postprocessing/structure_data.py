import pandas as pd
from typing import Dict, List

def process_pymupdf_output(pymupdf_data: Dict) -> List[Dict]:
    """Convert PyMuPDF output to standardized format"""
    results = []
    for block in pymupdf_data.get("blocks", []):
        results.append({
            "type": "text" if block["type"] == 0 else "image",
            "content": block.get("text", ""),
            "bbox": block.get("bbox", []),
            "source": "pymupdf"
        })
    return results

def process_donut_output(image, layout) -> List[Dict]:
    """Convert Donut model output to standardized format"""
    results = []
    for block in layout:
        results.append({
            "type": block.type,
            "content": block.text or "",
            "bbox": block.coordinates,
            "source": "donut"
        })
    return results

def clean_text(text: str) -> str:
    """Basic text cleaning"""
    import re
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    return text.strip()