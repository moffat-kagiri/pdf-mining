import os
import pandas as pd
from tqdm import tqdm
from src.utils import logger
from src.preprocessing import pdf_to_image
from src.extraction import layout_analysis, text_extraction
from src.postprocessing import process_pymupdf_output, process_donut_output

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

def process_batch(pdf_paths, output_dir, workers=1):
    dfs = []
    for path in tqdm(pdf_paths):
        dfs.append(process_single_pdf(path))
    
    final_df = pd.concat(dfs)
    final_df.to_excel(os.path.join(output_dir, "output.xlsx"), index=False)