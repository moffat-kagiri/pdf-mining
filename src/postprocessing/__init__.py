# src/postprocessing/__init__.py
from src.postprocessing.structure_data import (  # Changed from relative
    process_pymupdf_output,
    process_donut_output,
    clean_text
)

__all__ = ['process_pymupdf_output', 'process_donut_output', 'clean_text']