# This script converts PDF files to images using pdf2image.
# It is designed to handle scanned or handwritten PDFs by converting each page into an image.
# -*- coding: utf-8 -*-
from pdf2image import convert_from_path
import tempfile

def convert_pdf_to_images(pdf_path: str, dpi: int = 300) -> list:
    """Convert PDF pages to images (for scanned/handwritten PDFs)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        return convert_from_path(pdf_path, dpi=dpi, output_folder=temp_dir)