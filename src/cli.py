import argparse
import os
import logging
from typing import List
from pathlib import Path
from glob import glob
from pipeline.batch_processor import process_batch
from utils.config_loader import load_config
from preprocessing.pdf_to_image import convert_pdf_to_images
from preprocessing.image_enhancement import enhance_images
from extraction.layout_analysis import detect_layout
from extraction.text_extraction import extract_text
from extraction.table_handling import reconstruct_tables
from postprocessing.text_cleaner import clean_text
from postprocessing.structure_data import structure_table

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Batch PDF Processor")
    parser.add_argument("--input", required=True, help="PDF files or directory")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--config", default="./configs/default.yaml", help="Path to config file")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel processes")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    logger.info(f"Loaded configuration from {args.config}")

    # Resolve input paths
    if os.path.isdir(args.input):
        pdf_paths = glob(os.path.join(args.input, "*.pdf"))
    else:
        pdf_paths = glob(args.input)  # Supports wildcards (e.g., /data/*.pdf)

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Process each PDF
    for pdf_path in pdf_paths:
        logger.info(f"Processing {pdf_path}")

        # Step 1: Preprocessing
        images = convert_pdf_to_images(pdf_path, config)
        enhanced_images = enhance_images(images, config)

        # Step 2: Layout Analysis
        layout_elements = detect_layout(enhanced_images, config)

        # Step 3: Data Extraction
        text_data = extract_text(layout_elements, config)
        table_data = reconstruct_tables(layout_elements, config)

        # Step 4: Postprocessing
        cleaned_text = clean_text(text_data, config)
        structured_table = structure_table(table_data)

        # Step 5: Save Output
        output_file = os.path.join(args.output, f"{Path(pdf_path).stem}.xlsx")
        structured_table.to_excel(output_file, index=False)
        logger.info(f"Saved structured data to {output_file}")

    logger.info("Batch processing complete.")

if __name__ == "__main__":
    main()