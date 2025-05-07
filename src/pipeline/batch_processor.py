import os
import pandas as pd
from tqdm import tqdm
from src.utils import logger
from src.preprocessing import pdf_to_image
from src.extraction.layout_analysis import analyze_layout
from src.extraction.text_extraction import TextExtractor
from src.extraction.table_handling import reconstruct_table
from src.extraction.layout_analysis import analyze_layout
from src.postprocessing import (
    process_pymupdf_output, 
    process_donut_output,
    clean_text,
    text_cleaner
)
def process_pdf(pdf_path: str, config: dict, mode: str = 'auto'):
    extractor = TextExtractor(config)
    
    if mode == 'auto':
        text = extractor.extract(pdf_path)
    elif mode == 'direct':
        text = extractor._extract_direct_text(pdf_path)
    elif mode == 'ocr':
        text = extractor._extract_via_ocr(pdf_path)

def process_single_pdf(pdf_path):
    try:
        # Step 1: Convert PDF
        images = pdf_to_image.convert_pdf_to_images(pdf_path)
        
        # Step 2: Analyze Layout
        parser_type, layout_data = layout_analysis.analyze_pdf(pdf_path)
        
        # Step 3: Extract Content
        results = []
        for i, (img, layout) in enumerate(zip(images, layout_data)):
            if parser_type == "pymupdf":
                results.extend(process_pymupdf_output(layout))
            else:
                results.extend(process_donut_output(img, layout))
                
        return pd.DataFrame(results)
    
    except Exception as e:
        logger.error(f"Failed {pdf_path}: {str(e)}")
        return pd.DataFrame()
