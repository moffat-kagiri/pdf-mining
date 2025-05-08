# src/extraction/text_extraction.py
import logging
from typing import Optional, List, Union
import numpy as np
from PIL import Image
import cv2

# PDF processing
import fitz  # PyMuPDF
from pdf2image import convert_from_path

# OCR engines
import pytesseract
from easyocr import Reader

# Local imports
from .layout_analysis import analyze_layout

logger = logging.getLogger(__name__)

class TextExtractor:
    def __init__(self, config: dict):
        """Initialize with configuration settings"""
        self.config = config.get('text_extraction', {})
        self.ocr_config = config.get('ocr', {})
        self.layout_config = config.get('layout', {})
        self._validate_config()

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Main extraction method following the workflow:
        1. Try direct text extraction
        2. Fallback to image-based OCR if needed
        3. Return structured text or None if failed
        """
        # First attempt: Direct text extraction
        text = self._extract_with_pymupdf(pdf_path)
        if self._is_valid_text(text):
            logger.info("Successfully extracted text directly from PDF")
            return text

        # Fallback: Image-based OCR
        logger.warning("Direct extraction failed, attempting OCR fallback")
        return self._extract_with_ocr(pdf_path)

    def _extract_with_pymupdf(self, pdf_path: str) -> Optional[str]:
        """Extract text directly using PyMuPDF"""
        try:
            text = []
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    page_text = page.get_text("text")
                    if page_text:
                        text.append(page_text)
            return "\n".join(text) if text else None
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
            return None
        
    def _extract_with_ocr(self, pdf_path: str) -> Optional[str]:
        """Full OCR processing pipeline with proper config handling"""
        try:
            images = self._convert_pdf_to_images(pdf_path)
            if not images:
                return None

            # Process first page with config
            image = self._preprocess_image(images[0])
            layout = analyze_layout(image, self.config)  # Pass config
            return self._run_ocr_engine(image, layout)
            
        except Exception as e:
            logger.error(f"OCR pipeline failed: {str(e)}", exc_info=True)
            return None

    def _convert_pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to images with proper error handling"""
        try:
            return convert_from_path(
                pdf_path,
                dpi=self.config.get('dpi', 300),
                poppler_path=self.config.get('poppler_path'),
                thread_count=self.config.get('thread_count', 1)
            )
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {str(e)}")
            return []

    def _preprocess_image(self, image):
        """Enhanced preprocessing pipeline"""
        # Convert to grayscale
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=30)
        
        # Adaptive thresholding
        processed = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations
        kernel = np.ones((1,1), np.uint8)
        return cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)

    def _run_ocr_engine(self, image: np.ndarray, layout) -> str:
        """Run OCR with hybrid approach (Tesseract + EasyOCR fallback)"""
        try:
            # Try Tesseract first
            text = pytesseract.image_to_string(
                image,
                config=self.ocr_config.get('tesseract_config', '')
            )
            
            # Validate Tesseract results
            if len(text.strip()) > self.config.get('min_text_length', 50):
                return text
                
            # Fallback to EasyOCR if Tesseract results are poor
            reader = Reader(['en'])
            results = reader.readtext(image)
            return " ".join([res[1] for res in results])
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return ""

    def _is_valid_text(self, text: Optional[str]) -> bool:
        """Validate extracted text meets quality thresholds"""
        if not text or not text.strip():
            return False
        return len(text.strip()) >= self.config.get('min_text_length', 100)

    def _validate_config(self):
        """Ensure required configuration values are present"""
        if 'poppler_path' not in self.config:
            logger.warning("poppler_path not configured, PDF conversion may fail")


def extract_text(pdf_path: str, config: dict) -> Optional[str]:
    """Module-level function to match expected imports"""
    return TextExtractor(config).extract_text(pdf_path)


__all__ = ['TextExtractor', 'extract_text']