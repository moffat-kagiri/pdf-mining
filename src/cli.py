#!/usr/bin/env python
"""
PDF Mining CLI Tool
------------------
Command-line interface for extracting and analyzing text from PDF documents.
Supports both single file and batch processing with quality checks.

Key Features:
- Text extraction from PDFs (OCR and direct)
- Table detection and extraction
- Quality analysis and reporting
- Batch processing capabilities
"""

import argparse
import csv
import logging
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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

def ensure_directory_structure():
    """Create required directory structure for outputs and logs.
    
    Creates:
    - data/raw: For input PDFs
    - data/out/txt: For extracted text
    - data/out/csv: For extracted tables
    - data/out/quality: For quality reports
    - data/out/logs: For processing logs
    """
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/out/txt").mkdir(parents=True, exist_ok=True)
    Path("data/out/csv").mkdir(parents=True, exist_ok=True)
    Path("data/out/quality").mkdir(parents=True, exist_ok=True)
    Path("data/out/logs").mkdir(parents=True, exist_ok=True)

class QualityAnalyzer:
    """Analyzes and reports on the quality of extracted text content.
    
    Provides metrics including:
    - Character, word, and sentence counts
    - Line analysis
    - Text structure assessment (bullet points, whitespace)
    - Sample text preview
    """
    
    @staticmethod
    def calculate_metrics(text: str) -> Dict[str, float]:
        """Compute comprehensive quality metrics for extracted text.
        
        Args:
            text: The extracted text to analyze
            
        Returns:
            Dictionary of calculated metrics including counts and ratios
        """
        lines = text.splitlines()
        words = re.findall(r'\w+', text)
        sentences = re.split(r'[.!?]+', text)
        
        return {
            'char_count': len(text),
            'word_count': len(words),
            'line_count': len(lines),
            'sentence_count': len([s for s in sentences if len(s.strip()) > 0]),
            'avg_word_length': sum(len(w) for w in words)/len(words) if words else 0,
            'avg_words_per_line': len(words)/len(lines) if lines else 0,
            'whitespace_ratio': text.count(' ')/len(text) if text else 0,
            'bullet_point_count': text.count('•') + text.count('*')
        }
    
    @staticmethod
    def generate_report(text: str, pdf_path: str) -> str:
        """Generate human-readable quality report"""
        metrics = QualityAnalyzer.calculate_metrics(text)
        report = [
            f"Quality Report for {Path(pdf_path).name}",
            "=" * 40,
            f"Characters: {metrics['char_count']}",
            f"Words: {metrics['word_count']}",
            f"Lines: {metrics['line_count']}",
            f"Sentences: {metrics['sentence_count']}",
            f"Avg. word length: {metrics['avg_word_length']:.1f}",
            f"Avg. words/line: {metrics['avg_words_per_line']:.1f}",
            f"Bullet points: {metrics['bullet_point_count']}",
            "\nSample Text:",
            text[:500] + ("..." if len(text) > 500 else "")
        ]
        return "\n".join(report)

def load_config(config_path: str = None) -> dict:
    """Load configuration with fallback to defaults.
    
    Args:
        config_path: Optional path to YAML configuration file
        
    Returns:
        Dictionary containing configuration settings with defaults merged
    """
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
        'quality': {
            'min_word_count': 100,
            'min_bullet_points': 1
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
        return {**default_config, **yaml.safe_load(config_file.read_text())}
    except Exception as e:
        logger.error(f"Config load error: {str(e)}")
        return default_config

def process_content(text: str, config: dict) -> Tuple[str, Optional[list]]:
    """Process and clean extracted content, detect tables.
    
    Args:
        text: Raw extracted text
        config: Configuration dictionary
        
    Returns:
        Tuple of (cleaned_text, detected_tables)
    """
    from extraction.table_handling import detect_tables
    from postprocessing.text_cleaner import TextCleaner
    
    tables = detect_tables(text)
    cleaner = TextCleaner(config.get('text_cleaning', {}))
    return cleaner.clean(text), tables

def save_outputs(base_name: str, text: str, tables: list, pdf_path: str):
    """Save all processing outputs to respective directories.
    
    Saves:
    - Extracted text (.txt)
    - Detected tables (.csv)
    - Quality report (_qc.txt)
    - Prints summary to console
    """
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
        logger.info(f"Table saved to {csv_path}")

    # Save quality report
    report = QualityAnalyzer.generate_report(text, pdf_path)
    qc_path = f"data/out/quality/{base_name}_qc.txt"
    with open(qc_path, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.info(f"Quality report saved to {qc_path}")

    # Print summary to console
    print("\n" + "=" * 50)
    print(f"PROCESSING SUMMARY: {base_name}")
    print("=" * 50)
    print(report.split("Sample Text:")[0])  # Print metrics only
    print("=" * 50)

def process_pdf(input_path: Path, config: dict) -> bool:
    """Process a single PDF file through the complete pipeline.
    
    Workflow:
    1. Copy to raw directory if needed
    2. Extract text content
    3. Process and clean text
    4. Quality validation
    5. Save all outputs
    
    Args:
        input_path: Path to PDF file
        config: Configuration dictionary
        
    Returns:
        Boolean indicating success/failure
    """
    try:
        from extraction.text_extraction import TextExtractor
        
        # Ensure file is in raw directory
        raw_path = Path("data/raw") / input_path.name
        if not input_path.samefile(raw_path):
            shutil.copy(input_path, raw_path)
            input_path = raw_path

        # Extract content
        extractor = TextExtractor(config)
        raw_text = extractor.extract_text(str(input_path))
        if not raw_text:
            raise ValueError("No text extracted")

        # Process content
        clean_text, tables = process_content(raw_text, config)

        # Validate quality
        metrics = QualityAnalyzer.calculate_metrics(clean_text)
        if metrics['word_count'] < config['quality']['min_word_count']:
            logger.warning(f"Low word count: {metrics['word_count']}")

        # Save outputs
        save_outputs(input_path.stem, clean_text, tables, str(input_path))
        return True

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return False

def main():
    """Main entry point for the CLI application.
    
    Handles:
    - Command line argument parsing
    - Configuration loading
    - Single file or batch processing
    - Exit code management
    """
    ensure_directory_structure()
    
    parser = argparse.ArgumentParser(
        description="PDF Text Extraction with Quality Checking",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--input', required=True, help="Input PDF file or directory")
    parser.add_argument('--config', default='configs/ocr.yaml', help="Configuration file")
    args = parser.parse_args()

    config = load_config(args.config)
    input_path = Path(args.input)

    if input_path.is_file():
        success = process_pdf(input_path, config)
        sys.exit(0 if success else 1)
    else:
        processed = 0
        for pdf_file in input_path.glob("*.pdf"):
            if process_pdf(pdf_file, config):
                processed += 1
        logger.info(f"Processed {processed} files")
        sys.exit(0 if processed > 0 else 1)

if __name__ == "__main__":
    main()