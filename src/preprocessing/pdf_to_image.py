# This script converts PDF files to images using pdf2image.
# It is designed to handle scanned or handwritten PDFs by converting each page into an image.
# -*- coding: utf-8 -*-
from pdf2image import convert_from_path
import os
import logging
from pathlib import Path

def convert_pdf_to_images(pdf_path, config):
    # Define and verify poppler path
    poppler_path = Path(r"C:\Program Files\poppler\Library\bin")
    if not poppler_path.exists():
        raise EnvironmentError(
            "Poppler not found at: {}. Please install Poppler and verify path.".format(poppler_path)
        )
    
    dpi = config.get('dpi', 200)
    temp_dir = Path(config.get('temp_dir', './temp'))
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        return convert_from_path(
            pdf_path,
            dpi=dpi,
            output_folder=str(temp_dir),
            poppler_path=str(poppler_path)
        )
    except Exception as e:
        logging.error(f"PDF conversion failed: {str(e)}")
        raise