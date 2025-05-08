import os
from pathlib import Path
import tempfile
import shutil
from PIL import Image
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from utils.config_loader import config
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
    """Convert PDF file to list of images with enhanced error handling."""
    try:
        # Validate input file
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if pdf_path.stat().st_size == 0:
            raise ValueError(f"PDF file is empty: {pdf_path}")

        # Try PyMuPDF first
        try:
            logger.debug("Attempting conversion with PyMuPDF...")
            doc = fitz.open(pdf_path)
            if doc.needs_pass:
                raise ValueError(f"PDF is password protected: {pdf_path}")
                
            images = []
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
                
            if images:
                logger.info(f"Successfully converted {len(images)} pages using PyMuPDF")
                return images
                
        except Exception as e:
            logger.warning(f"PyMuPDF conversion failed, trying pdf2image: {str(e)}")

        # Fallback to pdf2image
        logger.debug("Attempting conversion with pdf2image...")
        poppler_path = get_poppler_path()
        images = convert_from_path(
            str(pdf_path),
            dpi=dpi,
            poppler_path=poppler_path,
            thread_count=2,
            grayscale=False  # Changed to color for better results
        )
        
        if not images:
            raise ValueError(f"No images extracted from PDF: {pdf_path}")
            
        logger.info(f"Successfully converted {len(images)} pages using pdf2image")
        return images

    except Exception as e:
        logger.error(f"PDF conversion failed for {pdf_path}: {str(e)}")
        raise