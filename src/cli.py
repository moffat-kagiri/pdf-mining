#!/usr/bin/env python
import argparse
import csv
import logging
import shutil
import sys
from pathlib import Path
from typing import Tuple, Optional

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/out/logs/processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_directory_structure():
    """Create all required directories with error handling"""
    required_dirs = [
        'data/raw',
        'data/out/txt',
        'data/out/csv',
        'data/out/logs'
    ]
    
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {str(e)}")
            sys.exit(1)

def load_config(config_path: str = None) -> dict:
    """Robust config loading with defaults"""
    default_config = {
        'text_extraction': {
            'min_text_length': 50,
            'poppler_path': None,
            'dpi': 300
        },
        'ocr': {
            'engine': 'hybrid',
            'denoise': True
        },
        'table_detection': {
            'min_columns': 2,
            'min_rows': 3
        }
    }
    
    if not config_path:
        return default_config

    try:
        import yaml
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return default_config
        return {**default_config, **yaml.safe_load(config_file.read_text())}
    except Exception as e:
        logger.error(f"Config load error: {str(e)}")
        return default_config

def process_content(text: str, config: dict) -> Tuple[str, Optional[list]]:
    """Detect and extract tables from content"""
    from extraction.table_handling import detect_tables
    from postprocessing.text_cleaner import TextCleaner
    
    tables = detect_tables(text, config.get('table_detection', {}))
    if tables:
        logger.info(f"Detected {len(tables)} tables")
    
    cleaner = TextCleaner(config.get('text_cleaning', {}))
    return cleaner.clean(text), tables

def save_outputs(base_name: str, text: str, tables: list):
    """Save outputs with proper formatting"""
    # Save text
    txt_path = f"data/out/txt/{base_name}.txt"
    try:
        with open(txt_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        logger.info(f"Text saved to {txt_path}")
    except Exception as e:
        logger.error(f"Failed to save text output: {str(e)}")

    # Save tables
    for i, table in enumerate(tables, 1):
        csv_path = f"data/out/csv/{base_name}_table{i}.csv"
        try:
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(table)
            logger.info(f"Table {i} saved to {csv_path}")
        except Exception as e:
            logger.error(f"Failed to save table {i}: {str(e)}")

def process_pdf(input_path: Path, config: dict) -> bool:
    """Process a single PDF file"""
    try:
        from extraction.text_extraction import TextExtractor
        
        # Stage 1: Ensure file is in raw directory
        raw_path = Path("data/raw") / input_path.name
        if not input_path.samefile(raw_path):
            shutil.copy(input_path, raw_path)
            input_path = raw_path

        # Stage 2: Content extraction
        extractor = TextExtractor(config)
        raw_text = extractor.extract_text(str(input_path))
        if not raw_text:
            raise ValueError("No text extracted")

        # Stage 3: Content processing
        clean_text, tables = process_content(raw_text, config)

        # Stage 4: Save outputs
        save_outputs(input_path.stem, clean_text, tables)
        return True

    except Exception as e:
        logger.error(f"Failed to process {input_path.name}: {str(e)}")
        return False

def main():
    # Initialize environment
    ensure_directory_structure()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="PDF text and table extraction tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--input', 
        required=True,
        help="Input PDF file path"
    )
    parser.add_argument(
        '--config',
        default='configs/ocr.yaml',
        help="Path to configuration file"
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    logger.info("Configuration loaded successfully")

    # Process file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    success = process_pdf(input_path, config)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()