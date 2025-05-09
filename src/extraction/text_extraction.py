import logging
import os
from typing import List, Dict, Optional
import numpy as np
from PIL import Image
import cv2
import fitz
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

class TextExtractor:
    def __init__(self, config: dict):
        self.config = config
        self.profile = config.get('profile', config.get('default_profile', 'standard'))
        self.profile_config = config['profiles'].get(self.profile, {})
        
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """Main extraction method with profile handling"""
        try:
            if self._should_use_direct_extraction():
                text = self._extract_with_pymupdf(pdf_path)
                if text and self._validate_text(text):
                    return text
            
            return self._extract_with_ocr(pdf_path)
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return None

    def _should_use_direct_extraction(self) -> bool:
        """Determine if direct text extraction should be attempted"""
        return self.profile != 'low_res' and not self.profile_config.get('force_ocr', False)

    def _extract_with_pymupdf(self, pdf_path: str) -> Optional[str]:
        """Direct text extraction for native PDFs"""
        try:
            with fitz.open(pdf_path) as doc:
                return "\n".join(page.get_text("text") for page in doc)
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
            return None

    def _extract_with_ocr(self, pdf_path: str) -> Optional[str]:
        """OCR-based extraction with image preprocessing"""
        try:
            images = self._pdf_to_images(pdf_path)
            if not images:
                return None
                
            processed_images = [self._preprocess_image(img) for img in images]
            return self._run_ocr(processed_images)
        except Exception as e:
            logger.error(f"OCR pipeline failed: {str(e)}")
            return None

    def _pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF to images with profile-specific settings"""
        dpi = self.profile_config.get('dpi', 300)
        try:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                poppler_path=self.config.get('poppler_path'),
                thread_count=1  # Safer for low-memory systems
            )
            return [np.array(img.convert('RGB')) for img in images]
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {str(e)}")
            return []

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Apply profile-specific image enhancements"""
        # Convert to grayscale
        processed = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Profile-specific processing
        if self.profile == 'low_res':
            processed = self._enhance_low_res(processed)
        else:
            if self.profile_config.get('denoise', True):
                processed = cv2.fastNlMeansDenoising(processed, h=30)
            if self.profile_config.get('binarize', False):
                _, processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        return processed

    def _enhance_low_res(self, image: np.ndarray) -> np.ndarray:
        """Specialized processing for low-resolution documents"""
        # Contrast enhancement
        contrast = self.profile_config.get('contrast_boost', 2.0)
        image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)
        
        # Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        image = cv2.filter2D(image, -1, kernel * self.profile_config.get('sharpening', 1.5))
        
        # Advanced binarization
        image = cv2.adaptiveThreshold(
            image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations
        kernel = np.ones((1,1), np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        return image

    def _run_ocr(self, images: List[np.ndarray]) -> str:
        """Run OCR with profile-specific settings"""
        try:
            import pytesseract
            from easyocr import Reader
            
            ocr_engine = self.profile_config.get('ocr_engine', 'hybrid')
            text = []
            
            for img in images:
                if ocr_engine in ['tesseract', 'hybrid']:
                    config = '--psm 6'
                    if self.profile == 'low_res':
                        config += ' -c tessedit_char_blacklist=||<>"\''
                    page_text = pytesseract.image_to_string(img, config=config)
                    text.append(page_text)
                
                if ocr_engine == 'hybrid' and len(page_text.strip()) < self.profile_config.get('min_text_length', 30):
                    reader = Reader(['en'])
                    results = reader.readtext(img)
                    text.append(" ".join([res[1] for res in results]))
            
            return "\n".join(text)
        except Exception as e:
            raise RuntimeError(f"OCR failed: {str(e)}")

    def _validate_text(self, text: str) -> bool:
        """Validate extracted text meets quality thresholds"""
        min_length = self.profile_config.get('min_text_length', 50)
        return len(text.strip()) >= min_length