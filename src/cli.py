import argparse
import os
import logging
from typing import List
from pathlib import Path
from glob import glob
from src.pipeline.batch_processor import process_batch
from src.utils.config_loader import load_config
from src.preprocessing.pdf_to_image import convert_pdf_to_images
from src.preprocessing.image_tools import enhance_image
from src.extraction.layout_analysis import detect_layout_elements
from src.extraction.text_extraction import extract_text
from src.extraction.table_handling import reconstruct_table
from src.postprocessing.text_cleaner import TextCleaner
from src.postprocessing.structure_data import structure_table

# Set environment variable for PyTorch
os.environ["TORCH_HOME"] = r"C:\Users\MOFFAT KAGIRI\.torch"

def parse_args():
    parser = argparse.ArgumentParser(description='PDF Mining Tool')
    parser.add_argument('--input', required=True, help='Input PDF file or directory')
    parser.add_argument('--output', default='./data/processed', help='Output directory')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Setup logging first
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, 
                       format='%(asctime)s - %(levelname)s - %(message)s')

    # Load configuration with proper error handling
    try:
        config = load_config(args.config)
        if args.config:
            logging.info(f"Loaded configuration from {args.config}")
        else:
            logging.info("Using default configuration")
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        return

    # Resolve input paths
    if os.path.isdir(args.input):
        pdf_paths = glob(os.path.join(args.input, "*.pdf"))
    else:
        pdf_paths = glob(args.input)  # Supports wildcards (e.g., /data/*.pdf)

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Process each PDF
    for pdf_path in pdf_paths:
        logging.info(f"Processing {pdf_path}")

        # Step 1: Preprocessing
        images = convert_pdf_to_images(pdf_path, config)
        enhanced_images = [enhance_image(image, config) for image in images]  # Process each image

        # Step 2: Layout Analysis
        layout_elements = detect_layout_elements(enhanced_images, config)

        # Step 3: Data Extraction
        text_data = extract_text(layout_elements, config)
        table_data = reconstruct_table(layout_elements, config)

        # Step 4: Postprocessing
        cleaned_text = TextCleaner.clean_text(text_data)
        structured_table = structure_table(table_data)

        # Step 5: Save Output
        output_file = os.path.join(args.output, f"{Path(pdf_path).stem}.xlsx")
        structured_table.to_excel(output_file, index=False)
        logging.info(f"Saved structured data to {output_file}")

    logging.info("Batch processing complete.")

if __name__ == "__main__":
    main()