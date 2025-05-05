# src/extraction/layout_analysis.py
import layoutparser as lp
import pymupdf
import numpy as np
import cv2
from ..utils.config_loader import config

def detect_layout_elements(pdf_path):
    """
    Unified function to detect layout elements from PDFs
    Returns: List of layout elements (text blocks, tables, etc.)
    """
    # Try native PDF parsing first
    try:
        with pymupdf.open(pdf_path) as doc:
            if any(page.get_text("dict") for page in doc):
                return _process_pymupdf_layout(doc)
    except Exception as e:
        print(f"PyMuPDF failed: {e}")
    
    # Fallback to Donut model
    try:
        return _process_donut_layout(pdf_path)
    except Exception as e:
        print(f"Donut failed: {e}")
        return []

def _process_pymupdf_layout(doc):
    """Process native PDF layout using PyMuPDF"""
    elements = []
    for page in doc:
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            elements.append({
                "type": "text" if block["type"] == 0 else "image",
                "bbox": block["bbox"],
                "text": block.get("text", "")
            })
    return elements

def _process_donut_layout(pdf_path):
    """Process scanned PDFs using Donut model"""
    model = lp.AutoLayoutModel("donut")
    images = convert_pdf_to_images(pdf_path)  # From your preprocessing module
    layouts = []
    for img in images:
        np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        layouts.extend(model.detect(np_img))
    return layouts

# Explicitly export the public function
__all__ = ['detect_layout_elements']