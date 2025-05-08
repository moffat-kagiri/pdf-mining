import argparse
import logging
import csv
from pathlib import Path
import shutil
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/out/logs/processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from src.extraction.text_extraction import TextExtractor
from src.extraction.table_handling import detect_tables
from src.postprocessing.text_cleaner import clean_text
from src.utils.config_loader import load_config

def ensure_directory_structure():
    """Create required directories"""
    Path("data/raw").mkdir(exist_ok=True)
    Path("data/out/txt").mkdir(parents=True, exist_ok=True)
    Path("data/out/csv").mkdir(parents=True, exist_ok=True)
    Path("data/out/logs").mkdir(parents=True, exist_ok=True)

def process_content(text: str) -> Tuple[str, Optional[list]]:
    """Detect and extract tables from content"""
    tables = detect_tables(text)
    if tables:
        logger.info(f"Detected {len(tables)} tables")
    return clean_text(text), tables

def save_outputs(base_name: str, text: str, tables: list):
    """Save both text and table outputs"""
    # Save text
    txt_path = f"data/out/txt/{base_name}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    logger.info(f"Text saved to {txt_path}")

    # Save tables
    for i, table in enumerate(tables, 1):
        csv_path = f"data/out/csv/{base_name}_table{i}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(table)
        logger.info(f"Table {i} saved to {csv_path}")

def process_pdf(input_path: Path, config: dict):
    """Process a single PDF file"""
    try:
        # Stage 1: Copy to raw directory (if not already there)
        if not input_path.parent.samefile(Path("data/raw")):
            raw_path = Path("data/raw") / input_path.name
            shutil.copy(input_path, raw_path)
            input_path = raw_path

        # Stage 2: Content extraction
        extractor = TextExtractor(config)
        raw_text = extractor.extract_text(str(input_path))
        if not raw_text:
            raise ValueError("No text extracted")

        # Stage 3: Content processing
        clean_text, tables = process_content(raw_text)

        # Stage 4: Save outputs
        base_name = input_path.stem
        save_outputs(base_name, clean_text, tables)

        return True

    except Exception as e:
        logger.error(f"Failed to process {input_path.name}: {str(e)}")
        return False

def main():
    ensure_directory_structure()
    parser = argparse.ArgumentParser(description="PDF Mining Tool")
    
    parser.add_argument('--input', required=True,
                      help="Input PDF file or directory")
    parser.add_argument('--config', default='configs/ocr.yaml',
                      help="Configuration file path")
    
    args = parser.parse_args()
    config = load_config(args.config)
    input_path = Path(args.input)

    if input_path.is_file():
        success = process_pdf(input_path, config)
        exit(0 if success else 1)
    else:
        processed = sum(process_pdf(pdf, config) 
                       for pdf in Path("raw").glob("*.pdf"))
        logger.info(f"Processed {processed} files")
        exit(0 if processed > 0 else 1)

if __name__ == "__main__":
    main()