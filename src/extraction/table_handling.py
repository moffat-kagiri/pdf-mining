# This module handles the extraction and reconstruction of tables from images.
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from src.extraction.text_extraction import extract_text

def reconstruct_table(table_image: np.ndarray, config) -> pd.DataFrame:
    """Convert table image to DataFrame using OCR and heuristics."""
    text = extract_text(table_image)
    if text is None:
        return pd.DataFrame()  # Return empty DataFrame if no text was extracted
    # Add logic to split into rows/columns (e.g., regex or OpenCV line detection)
    return pd.DataFrame([row.split("|") for row in text.split("\n")])