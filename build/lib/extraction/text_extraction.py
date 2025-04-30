# -*- coding: utf-8 -*-
# This module extracts text from images using Tesseract or EasyOCR.
from typing import Optional
import numpy as np
import pytesseract
import logging
from utils.config_loader import load_ocr_config

def extract_text(image: np.ndarray, engine: str = "tesseract") -> Optional[str]:
    """
    Extract text from image using specified OCR engine.
    
    Args:
        image: numpy array containing the image
        engine: OCR engine to use ("tesseract" supported)
    
    Returns:
        Extracted text or empty string if extraction fails
    """
    config = load_ocr_config()
    
    try:
        if engine == "tesseract":
            return pytesseract.image_to_string(
                image,
                lang="+".join(config["tesseract"]["languages"]),
                config=f'--psm {config["tesseract"]["psm"]} --oem {config["tesseract"]["oem"]}'
            )
        else:
            raise ValueError(f"Unsupported OCR engine: {engine}")
            
    except pytesseract.TesseractError as e:
        logging.error(f"Tesseract OCR failed: {str(e)}")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error during text extraction: {str(e)}")
        return ""