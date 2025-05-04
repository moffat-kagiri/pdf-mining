# src/preprocessing/pdf_to_image.py
import os
from pdf2image import convert_from_path

def get_poppler_path():
    """Locate Poppler binaries installed by Chocolatey"""
    paths = [
        r"C:\Program Files\poppler-25.04.0\Library\bin",  # Chocolatey install path
        r"C:\Program Files\poppler\Library\bin"           # Alternate path
    ]
    for path in paths:
        if os.path.exists(os.path.join(path, "pdftoppm.exe")):
            return path
    raise RuntimeError(
        "Poppler not found. Please run: choco install poppler"
    )

def convert_pdf_to_images(pdf_path, dpi=200):
    return convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=get_poppler_path(),
        thread_count=2  # Safer for 4-core CPU
    )