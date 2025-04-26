# -*- coding: utf-8 -*-
# This script enhances images for better OCR results.
import cv2
import numpy as np

def enhance_image(image: np.ndarray) -> np.ndarray:
    """Preprocess images for better OCR results."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    return cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]