# src/extraction/text_extraction.py
import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def ensure_cv2_image(image):
    """Convert any image format to OpenCV-compatible numpy array"""
    if isinstance(image, np.ndarray):
        return image
    try:
        if isinstance(image, Image.Image):
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image, str):  # File path
            return cv2.imread(image)
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
    except Exception as e:
        logger.error(f"Image conversion failed: {str(e)}")
        raise

def extract_text(image, engine="auto"):
    """Extract text from image with format validation"""
    try:
        cv_img = ensure_cv2_image(image)
        if cv_img is None:
            raise ValueError("Invalid image input")
            
        # Rest of your OCR logic...
        if engine == "auto":
            text = pytesseract.image_to_string(cv_img)
            if len(text.strip()) > 10:
                return text
            return " ".join([res[1] for res in easyocr_reader.readtext(cv_img)])
            
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        return ""