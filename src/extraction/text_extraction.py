import fitz
from pdf2image import convert_from_path
import logging
from typing import Optional, List
import numpy as np

class TextExtractor:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def extract(self, pdf_path: str) -> Optional[str]:
        """Main extraction method with fallback logic"""
        # First attempt direct text extraction
        direct_text = self._extract_direct_text(pdf_path)
        if direct_text and self._validate_text(direct_text):
            return direct_text
            
        # Fallback to image-based OCR
        return self._extract_via_ocr(pdf_path)

    def _extract_direct_text(self, pdf_path: str) -> Optional[str]:
        """Direct text extraction using PyMuPDF"""
        try:
            text = ""
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text if text.strip() else None
        except Exception as e:
            self.logger.warning(f"Direct text extraction failed: {str(e)}")
            return None

    def _extract_via_ocr(self, pdf_path: str) -> Optional[str]:
        """Image-based OCR fallback"""
        try:
            images = self._pdf_to_images(pdf_path)
            if not images:
                return None
            return self._run_ocr(images[0])
        except Exception as e:
            self.logger.error(f"OCR fallback failed: {str(e)}")
            return None

    def _pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """PDF to image conversion"""
        try:
            return convert_from_path(
                pdf_path,
                poppler_path=self.config.get('poppler_path')
            )
        except Exception as e:
            self.logger.error(f"PDF to image conversion failed: {str(e)}")
            return []

    def _validate_text(self, text: str) -> bool:
        """Validate extracted text quality"""
        return len(text.strip()) > self.config.get('min_text_length', 50)

    def _run_ocr(self, image: np.ndarray) -> str:
        """Your existing OCR implementation"""
        # Implement your OCR logic here
        return "OCR Result Placeholder"

# Explicit exports
__all__ = ['TextExtractor']