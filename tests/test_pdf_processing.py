# -*- coding: utf-8 -*-
# This script tests the PDF to image conversion functionality.
# It is designed to ensure that the conversion process works correctly and produces images of the expected size.
import pytest
from src.preprocessing.pdf_to_image import convert_pdf_to_images

def test_pdf_conversion():
    images = convert_pdf_to_images("tests/sample.pdf")
    assert len(images) > 0
    assert images[0].size == (1654, 2340)  # Verify dimensions