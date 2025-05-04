import os
from pdf2image import convert_from_path
from ..utils.config_loader import load_config

config = load_config()

def convert_pdf_to_images(pdf_path, dpi=200):
    try:
        return convert_from_path(
            pdf_path,
            dpi=dpi,
            poppler_path=config["paths"]["poppler_path"],
            thread_count=2,
            grayscale=True  # Reduces memory usage
        )
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {str(e)}")