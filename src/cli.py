import argparse
import os
import logging
from typing import List
from pathlib import Path
from glob import glob
from pipeline.batch_processor import process_batch

def main():
    parser = argparse.ArgumentParser(description="Batch PDF Processor")
    parser.add_argument("--input", required=True, help="PDF files or directory")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--workers", type=int, help="Number of parallel processes")
    args = parser.parse_args()

    # Resolve input paths
    if os.path.isdir(args.input):
        pdf_paths = glob(os.path.join(args.input, "*.pdf"))
    else:
        pdf_paths = glob(args.input)  # Supports wildcards (e.g., /data/*.pdf)

    process_batch(pdf_paths, args.output, args.workers)

if __name__ == "__main__":
    main()