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


def detect_layout_elements(image, config=None):
    """Detect layout elements in an image or PDF path.
    
    Args:
        image: Image array or path to PDF file
        config: Optional configuration dictionary
    
    Returns:
        List of detected layout elements
    """
    elements = []
    
    try:
        if isinstance(image, str):  # PDF path
            if config and config.get('layout', {}).get('model') == 'donut':
                return _process_donut_layout(image)
            else:
                doc = pymupdf.open(image)
                return _process_pymupdf_layout(doc)
        else:  # Image array
            # Example PyMuPDF processing
            layout = {
                'type': 'text',
                'bbox': [0, 0, image.shape[1], image.shape[0]],
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

# Step 2: Layout Analysis
def analyze_layout(pdf_path, config):
    from ..preprocessing.image_tools import enhance_image
    
    enhanced_images = enhance_image(pdf_path, config)
    try:
        layout_elements = detect_layout_elements(enhanced_images[0], config)
        if not layout_elements:
            logging.error(f"No layout elements detected in {pdf_path}")
            return None
    except IndexError:
        logging.error(f"No valid images found in {pdf_path}")
        return None
    except Exception as e:
        logging.error(f"Layout analysis failed for {pdf_path}: {str(e)}")
        return None

# Explicitly export the public function
__all__ = ['detect_layout_elements']