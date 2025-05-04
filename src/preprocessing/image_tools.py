# -*- coding: utf-8 -*-
# This script enhances images for better OCR results.
import cv2
import numpy as np

def enhance_image(image, config):
    """
    Enhance the quality of an image based on the configuration.

    Args:
        image (numpy.ndarray): The input image.
        config (dict): Configuration settings for enhancement.

    Returns:
        numpy.ndarray: The enhanced image.
    """
    if config.get("image_enhancement", {}).get("denoise", False):
        image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    if config.get("image_enhancement", {}).get("binarize", False):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return image