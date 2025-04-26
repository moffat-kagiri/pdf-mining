import os
from multiprocessing import Pool, cpu_count
from typing import List
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.retry import create_retry_decorator, RetryConfig
from src.utils.retry import retry_ocr, retry_network

pdf_retry = create_retry_decorator(
    RetryConfig(
        max_attempts=4,
        min_wait=1,
        max_wait=20,
        retry_on=PDFSyntaxError
    )
)

def download_file(url: str, dest: str) -> None:
    """Download a file from a URL to a local destination."""
    import requests
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download file: {response.status_code}")
@pdf_retry
def download_pdf(url: str, dest: str) -> None:
    """Download a PDF file from a URL."""
    download_file(url, dest)

@pdf_retry
def parse_pdf(path):
    with pdfplumber.open(path) as pdf:
        return pdf.pages[0].extract_text()
    
try:
    from src.preprocessing.pdf_to_image import convert_pdf_to_images
    from src.extraction.layout_analysis import detect_layout_elements
    from src.postprocessing.structure_data import structure_table as to_structured_table
    import logging

    def setup_logger(name: str) -> logging.Logger:
        """
        Set up a logger with specified configuration.
        
        Args:
            name: The name of the logger

        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(name)
        
        if not logger.handlers:  # Avoid adding handlers multiple times
            logger.setLevel(logging.INFO)
            
            # Create console handler with formatting
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(handler)
        
        return logger
except ImportError as e:
    logging.error(f"Failed to import required modules: {str(e)}")
    raise

logger = setup_logger("batch_processor")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def process_single_pdf(pdf_path: str, output_dir: str) -> None:
    """Process one PDF and save results to output_dir."""
    try:
        # 1. Convert PDF to images (handles scanned/handwritten)
        images = convert_pdf_to_images(pdf_path)
        
        # 2. Extract and structure data
        all_data = []
        for img in images:
            img_np = np.array(img)  # Convert PIL to OpenCV format
            del img  # Free memory immediately
            layout = detect_layout_elements(img_np)
            structured_data = to_structured_table(layout)
            all_data.append(structured_data)
        
        # 3. Save output
        output_path = os.path.join(output_dir, f"{os.path.basename(pdf_path)}_output.xlsx")
        pd.concat(all_data).to_excel(output_path, index=False)
        logger.info(f"Processed {pdf_path} -> {output_path}")

    except Exception as e:
        logger.error(f"Failed to process {pdf_path}: {str(e)}")


from typing import Optional
def process_batch(pdf_paths: List[str], output_dir: str, workers: Optional[int] = None) -> None:
    """Parallel processing of multiple PDFs."""
    workers = workers or max(1, cpu_count() - 1)  # Leave 1 core free
    os.makedirs(output_dir, exist_ok=True)
    with Pool(processes=workers) as pool:
        list(tqdm(
            pool.imap_unordered(
                lambda x: process_single_pdf(*x),
                [(pdf, output_dir) for pdf in pdf_paths]
            ),
            total=len(pdf_paths),
            desc="Processing PDFs"
        ))