# PDF-mining

A robust Python tool to automatically extract structured data from PDFs—including bank statements, invoices, articles, and forms—while handling typed text, scanned documents, and handwritten notes. Preserves layout, ignores stamps/signatures (saved as images), and outputs clean Excel files.

[![Demo](https://img.shields.io/badge/Demo-Try%20It%20Out-blue)](https://github.com/MoffatKagiri/pdf-mining)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-orange)](%23license)

## Key Features

- **Universal PDF Support:** Handles typed, scanned, and handwritten PDFs using OCR and ML-based layout analysis.
- **Parallel Batch Processing:** Processes large directories of PDFs in parallel with configurable worker count.
- **Configurable Pipeline:** YAML-based configuration for extraction, cleaning, and output options.
- **Smart Data Extraction:** Converts paragraphs and tables into structured CSV/Excel, preserving layout.
- **Signature & Stamp Handling:** Detects and isolates stamps/signatures, saving them as images.
- **Detailed Logging & Reporting:** Logs progress and errors, and generates batch reports.
- **Progress Tracking:** See real-time progress and summary statistics.

## Use Cases

- **Banking:** Extract transactions from certified statements.
- **Legal/Research:** Scrape text from articles/contracts into tables.
- **Archival:** Digitize handwritten forms or historical documents.

## First-Time Setup

1. **Create directory structure:**

   ```bash
   mkdir -p data/raw data/out/txt data/out/csv data/out/logs data/temp
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   - For OCR and scanned PDFs, ensure [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [Poppler](https://poppler.freedesktop.org/) are installed (on Windows, use Chocolatey: `choco install tesseract poppler`).

## Quick Start

**Process a directory of PDFs:**

```bash
python src/cli.py --input data/raw/batch --config configs/batch_config.yaml
```

**Process with 12 workers:**

```bash
python src/cli.py --input data/raw/batch --workers 12
```

**Process a single large file:**

```bash
python src/cli.py --input data/raw/large_report.pdf --workers 4
```

## Example Output

| Content Type |                        Text |
| :----------- | --------------------------: |
| Header       |     BANK OF XYZ - STATEMENT |
| Paragraph    |        Account Summary: ... |
| Table        | [Date, Amount, Description] |

- **Text output:** `data/out/txt/{filename}.txt`
- **Structured CSV:** `data/out/csv/{filename}.csv`
- **Logs & reports:** `data/out/logs/`
- **Signatures/stamps:** Saved as images (if detected)

## How It Works

1. **PDF Analysis:** Detects text and scanned content using PyMuPDF, pdf2image, and Tesseract OCR.
2. **Layout Parsing:** Uses LayoutParser and ML models to identify headings, paragraphs, and tables.
3. **Text Cleaning:** Cleans and normalizes extracted text.
4. **Signature Removal:** (Optional) YOLOv5 model isolates stamps/signatures.
5. **Structured Export:** Outputs clean CSV and Excel files with separated data and images.
6. **Batch Reporting:** Generates a summary report after each run.

## Configuration

- Edit `configs/batch_config.yaml` to customize extraction, cleaning, and output options.
- Command-line arguments override config file settings (e.g., `--workers`).

## Contribute & Train

- **Improve Accuracy:** Annotate your PDFs with Label Studio and retrain models.
- **Add New Formats:** Fork and extend the pipeline for custom documents (e.g., receipts).

**Test a single file:**

```bash
python src/cli.py --input "./tests/data/simple.pdf"
```

## License

MIT © 2024 Moffat Kagiri
