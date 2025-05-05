import layoutparser as lp
import fitz
import numpy as np
import cv2
import pymupdf
from src.utils.config_loader import load_config  # Changed from relative
from src.preprocessing.pdf_to_image import convert_pdf_to_images  # Changed from relative

config = load_config()

def analyze_pdf(pdf_path):
    # Try native PDF parsing first
    try:
        with pymupdf.open(pdf_path) as doc:
            if any(page.get_text("dict") for page in doc):
                return "pymupdf", [page.get_text("dict") for page in doc]
    except:
        pass
    
    # Fallback to Donut model for scanned PDFs
    try:
        model = lp.AutoLayoutModel("donut", label_map={0:"text", 1:"table"})
        images = convert_pdf_to_images(pdf_path)
        return "donut", [model.detect(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)) for img in images]
    except Exception as e:
        raise RuntimeError(f"Layout analysis failed: {str(e)}")
                           