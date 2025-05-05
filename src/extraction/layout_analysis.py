# src/extraction/layout_analysis.py
from tkinter import Image
import layoutparser as lp
import logging
import pymupdf
import numpy as np
import cv2
from ..utils.config_loader import config
from ..preprocessing.pdf_to_image import convert_pdf_to_images

logger = logging.getLogger(__name__)


def detect_layout_elements(image):
    elements = []
    
    # Example PyMuPDF processing
    try:
        # Convert image to PDF-like structure
        layout = {
            'type': 'text',
            'bbox': [0, 0, image.width, image.height],
            'content': '',
            'image': image  # Keep original image for OCR
        }
        elements.append(layout)
        
    except Exception as e:
        logger.error(f"Layout analysis failed: {str(e)}")
    
    return elements

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