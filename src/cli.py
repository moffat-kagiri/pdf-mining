#!/usr/bin/env python
import argparse
import csv
import logging
import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

# Configure logging to both file and console
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
    """Create required directories for raw data, outputs, and logs if they don't exist."""
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/out/txt").mkdir(parents=True, exist_ok=True)
    Path("data/out/csv").mkdir(parents=True, exist_ok=True)
    Path("data/out/logs").mkdir(parents=True, exist_ok=True)

class ContentParser:
    """Handles text parsing and conversion to structured formats."""

    @staticmethod
    def parse_to_paragraphs(text: str) -> List[List[str]]:
        """
        Convert text to paragraph-based CSV rows.
        - Splits text into paragraphs on empty lines.
        - If a line contains pipes ('|'), splits into columns.
        - Returns a list of rows, each row is a list of columns.
        """
        paragraphs = []
        current_paragraph = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:  # Empty line indicates paragraph break
                if current_paragraph:
                    paragraphs.append([" ".join(current_paragraph)])
                    current_paragraph = []
                continue

            # Handle pipe-delimited content as table rows
            if "|" in stripped:
                pipe_split = [s.strip() for s in stripped.split("|")]
                if current_paragraph:
                    paragraphs.append([" ".join(current_paragraph)])
                    current_paragraph = []
                paragraphs.append(pipe_split)
            else:
                current_paragraph.append(stripped)

        if current_paragraph:  # Add last paragraph if present
            paragraphs.append([" ".join(current_paragraph)])

        return paragraphs

def load_config(config_path: str = None) -> dict:
    """
    Load configuration from YAML file if provided, otherwise use defaults.
    Returns a dictionary with configuration settings.
    """
    default_config = {
        'text_extraction': {
            'min_text_length': 50,
            'poppler_path': None,
            'dpi': 300
        },
        'parsing': {
            'pipe_as_tab': True,
            'max_columns': 10
        }
    }

    if not config_path:
        return default_config

    try:
        import yaml
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}")
            return default_config
        # Merge loaded config with defaults
        return {**default_config, **yaml.safe_load(config_file.read_text())}
    except Exception as e:
        logger.error(f"Config load error: {str(e)}")
        return default_config

def save_outputs(base_name: str, text: str, config: dict):
    """
    Save both the raw extracted text and the structured CSV output.
    - Writes text to data/out/txt/{base_name}.txt
    - Writes structured CSV to data/out/csv/{base_name}.csv
    """
    # Save raw text output
    txt_path = f"data/out/txt/{base_name}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    logger.info(f"Text saved to {txt_path}")

    # Parse text into structured paragraphs/rows
    parser = ContentParser()
    paragraphs = parser.parse_to_paragraphs(text)

    csv_path = f"data/out/csv/{base_name}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')

        # Determine the maximum number of columns for the CSV header
        max_columns = min(
            max(len(row) for row in paragraphs),
            config['parsing']['max_columns']
        )
        writer.writerow([f"Column_{i+1}" for i in range(max_columns)])

        # Write each row, padding with empty strings if needed
        for row in paragraphs:
            padded_row = row + [''] * (max_columns - len(row))
            writer.writerow(padded_row)

    logger.info(f"Structured CSV saved to {csv_path}")
    logger.info(f"Detected {len(paragraphs)} paragraphs/rows")

def process_pdf(input_path: Path, config: dict) -> bool:
    """
    Process a single PDF file:
    - Copies the PDF to the raw data directory if needed.
    - Extracts text using the TextExtractor.
    - Saves both text and structured CSV outputs.
    Returns True on success, False on failure.
    """
    try:
        from extraction.text_extraction import TextExtractor

        # Ensure file is in raw directory for consistency
        raw_path = Path("data/raw") / input_path.name
        if not input_path.samefile(raw_path):
            shutil.copy(input_path, raw_path)
            input_path = raw_path

        # Extract text content from PDF
        extractor = TextExtractor(config)
        text = extractor.extract_text(str(input_path))
        if not text:
            raise ValueError("No text extracted")

        # Save outputs (text and CSV)
        save_outputs(input_path.stem, text, config)
        return True

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return False

def main():
    """
    Main entry point for the CLI tool.
    - Ensures required directories exist.
    - Parses command-line arguments.
    - Loads configuration.
    - Processes the input PDF.
    """
    ensure_directory_structure()

    parser = argparse.ArgumentParser(
        description="PDF to Text and Structured CSV Converter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--input', required=True, help="Input PDF file")
    parser.add_argument('--config', default='configs/ocr.yaml', help="Config file")
    args = parser.parse_args()

    config = load_config(args.config)
    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    success = process_pdf(input_path, config)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()