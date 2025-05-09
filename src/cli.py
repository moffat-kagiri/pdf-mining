#!/usr/bin/env python
"""Large-scale PDF Processing Pipeline for batch text extraction and cleaning.
This module provides a command-line interface and core functionality for processing
PDF files in parallel, extracting text content, cleaning it, and saving results.
Key Features:
- Parallel PDF processing with configurable number of workers 
- Directory rotation for organized output storage
- Detailed logging and reporting
- YAML configuration support
- Progress tracking and error handling
Classes:
    PDFProcessor: Core PDF batch processing engine with parallel execution support
Functions:
    load_config: Load and merge YAML configuration with defaults
    setup_directories: Create required directory structure
    main: CLI entry point and orchestration
Command Line Arguments:
    --input: Path to input PDF file or directory (required)
    --config: Path to YAML config file (default: configs/batch_config.yaml) 
    --workers: Override number of worker processes
Example Usage:
    python cli.py --input /path/to/pdfs --workers 4
Directory Structure:
    data/
        raw/
            batch/  # Input PDFs
        out/
            logs/  # Processing logs and reports
            YYYYMMDD/  # Daily output folders
"""
import argparse
import csv
import logging
import multiprocessing
import os
import shutil
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/out/logs/batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Core PDF processing engine with parallelization support"""
    
    def __init__(self, config: dict):
        self.config = config
        self.max_workers = config.get('max_workers', os.cpu_count() - 1 or 1)
        self.chunk_size = config.get('chunk_size', 10)
        
    def process_batch(self, pdf_files: List[Path]) -> dict:
        """Process multiple PDFs in parallel"""
        from extraction.text_extraction import TextExtractor
        from postprocessing.text_cleaner import TextCleaner
        
        results = {
            'processed': 0,
            'failed': 0,
            'files': []
        }
        
        def _process_file(pdf_path: Path):
            try:
                extractor = TextExtractor(self.config)
                text = extractor.extract_text(str(pdf_path))
                if not text:
                    return None
                
                cleaner = TextCleaner(self.config.get('text_cleaning', {}))
                clean_text = cleaner.clean(text)
                
                output_path = self._save_outputs(pdf_path.stem, clean_text)
                return {
                    'input': str(pdf_path),
                    'output': output_path,
                    'status': 'success'
                }
            except Exception as e:
                logger.error(f"Failed {pdf_path.name}: {str(e)}")
                return {
                    'input': str(pdf_path),
                    'error': str(e),
                    'status': 'failed'
                }
        
        with multiprocessing.Pool(processes=self.max_workers) as pool:
            for result in pool.imap_unordered(_process_file, pdf_files, chunksize=self.chunk_size):
                if result:
                    results['files'].append(result)
                    if result['status'] == 'success':
                        results['processed'] += 1
                    else:
                        results['failed'] += 1
        
        return results
    
    def _save_outputs(self, base_name: str, text: str) -> str:
        """Save outputs with directory rotation"""
        # Create dated output directory
        date_str = time.strftime("%Y%m%d")
        output_dir = Path(f"data/out/{date_str}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save text
        txt_path = output_dir / f"{base_name}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return str(txt_path)

def load_config(config_path: str = None) -> dict:
    """Load configuration with batch processing defaults"""
    default_config = {
        'max_workers': os.cpu_count() - 1 or 1,
        'chunk_size': 10,
        'text_extraction': {
            'min_text_length': 50,
            'dpi': 300,
            'poppler_path': None
        },
        'text_cleaning': {
            'preserve_newlines': True,
            'fix_bullets': True
        }
    }
    
    if not config_path:
        return default_config
        
    try:
        import yaml
        with open(config_path, 'r') as f:
            return {**default_config, **yaml.safe_load(f)}
    except Exception as e:
        logger.error(f"Config error: {str(e)}")
        return default_config

def setup_directories():
    """Ensure directory structure exists"""
    Path("data/raw/batch").mkdir(parents=True, exist_ok=True)
    Path("data/out/logs").mkdir(parents=True, exist_ok=True)

def main():
    setup_directories()
    
    parser = argparse.ArgumentParser(
        description="Large-scale PDF Processing Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--input',
        required=True,
        help="Input PDF file or directory"
    )
    parser.add_argument(
        '--config',
        default='configs/batch_config.yaml',
        help="Configuration file"
    )
    parser.add_argument(
        '--workers',
        type=int,
        help="Override max worker processes"
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    if args.workers:
        config['max_workers'] = args.workers
    
    processor = PDFProcessor(config)
    input_path = Path(args.input)

    # Prepare file list
    if input_path.is_file():
        pdf_files = [input_path]
    else:
        pdf_files = list(input_path.glob("*.pdf")) + list(input_path.glob("**/*.pdf"))
    
    if not pdf_files:
        logger.error("No PDF files found")
        sys.exit(1)

    logger.info(f"Starting batch processing of {len(pdf_files)} files with {config['max_workers']} workers")

    # Process batch
    start_time = time.time()
    results = processor.process_batch(pdf_files)
    elapsed = time.time() - start_time

    # Generate report
    report = (
        f"\n{'='*40}\n"
        f"BATCH PROCESSING REPORT\n"
        f"{'='*40}\n"
        f"Total files: {len(pdf_files)}\n"
        f"Processed: {results['processed']}\n"
        f"Failed: {results['failed']}\n"
        f"Elapsed time: {elapsed:.2f} seconds\n"
        f"Files/sec: {len(pdf_files)/elapsed:.2f}\n"
        f"{'='*40}"
    )
    
    logger.info(report)
    
    # Save detailed report
    report_path = Path(f"data/out/logs/batch_report_{time.strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_path, 'w') as f:
        f.write(report + "\n\n")
        for file in results['files']:
            f.write(f"{file['input']} - {file['status']}\n")
            if file['status'] == 'failed':
                f.write(f"ERROR: {file['error']}\n")
    
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    multiprocessing.freeze_support()  # For Windows executable support
    main()