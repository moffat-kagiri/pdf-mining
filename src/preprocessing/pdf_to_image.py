# src/preprocessing/pdf_to_image.py
import os
from pdf2image import convert_from_path
from ..utils.config_loader import config
import logging

logger = logging.getLogger(__name__)

def get_poppler_path():
    """Find poppler binaries with multiple fallback locations"""
    paths = [
        r"C:\Program Files\poppler-25.04.0\Library\bin",  # Chocolatey default
        r"C:\Program Files\poppler\Library\bin",          # Alternate install path
        os.environ.get("POPPLER_PATH", ""),               # Environment variable
        config["paths"]["poppler_path"]                   # Config file
    ]
    
    for path in paths:
        if path and os.path.exists(os.path.join(path, "pdftoppm.exe")):
            logger.info(f"Using poppler at: {path}")
            return path
    
    raise RuntimeError(
        "Poppler not found. Please install via:\n"
        "1. Chocolatey: 'choco install poppler'\n"
        "2. OR download from: https://github.com/oschwartz10612/poppler-windows/releases/\n"
        "3. Then add to PATH or set POPPLER_PATH environment variable"
    )

def convert_pdf_to_images(pdf_path, dpi=200):
    try:
        poppler_path = get_poppler_path()
        return convert_from_path(
            pdf_path,
            dpi=dpi,
            poppler_path=poppler_path,
            thread_count=2,
            grayscale=True
        )
    except Exception as e:
        logger.error(f"PDF conversion failed: {str(e)}")
        raise