# PDF-mining

A robust Python tool to automatically extract structured data from PDFs—including bank statements, invoices, articles, and forms—while handling typed text, scanned documents, and handwritten notes. Preserves layout, ignores stamps/signatures (saved as images), and outputs clean Excel files.

[![Demo](https://img.shields.io/badge/Demo-Try%20It%20Out-blue)](https://github.com/MoffatKagiri/pdf-mining)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-orange)](%23license)

A robust Python tool to automatically extract structured data from PDFs—including bank statements, invoices, articles, and forms—while handling typed text, scanned documents, and handwritten notes. Preserves layout, ignores stamps/signatures (saved as images), and outputs clean Excel files.

## Key Features

✅ Universal PDF Support

- Works with typed text, scanned images, and handwritten content (OCR-powered).
- Handles complex layouts (tables, paragraphs, headings) using ML-based detection.

✅ Smart Data Extraction

- Converts paragraphs/articles into single-column tables with headers.
- Extracts tables accurately (even from scanned docs) via layout analysis.

✅ Signature & Stamp Handling

- Detects and isolates stamps/signatures, saving them in a separate Excel tab as images.

✅ Machine Learning-Powered

- Trainable on custom datasets (e.g., bank statements, invoices) for improved accuracy.
- Pre-trained models included for quick deployment.

✅ Excel & CSV Output

- Exports structured data to Excel with multi-tab support (data + images).

## Use Cases

Banking: Extract transactions from certified statements.

Legal/Research: Scrape text from articles/contracts into tables.

Archival: Digitize handwritten forms or historical documents.

## First-Time Setup

1. Create directory structure:

   ```bash
   mkdir -p data/{raw,out/{txt,csv,logs},temp}
   ```

## Quick Start

Process a directory:

```bash
python src/cli.py --input data/raw/batch --config configs/batch_config.yaml
```

Process with 12 workers:

```bash
python src/cli.py --input data/raw/batch --workers 12
```

Process single large file:python src/cli.py --input data/raw/large_report.pdf --workers 4

## Example Output

| Content Type |                        Text |
| :----------- | --------------------------: |
| Header       |     BANK OF XYZ - STATEMENT |
| Paragraph    |        Account Summary: ... |
| Table        | [Date, Amount, Description] |

(Signatures/stamps saved in Images tab)

## How It Works

PDF Analysis: Detects text/scanned content using pdfplumber + Tesseract.

Layout Parsing: Uses LayoutParser to identify headings, paragraphs, and tables.

Signature Removal: YOLOv5 model isolates stamps/signatures.

Structured Export: Outputs clean Excel files with separated data and images.

## Contribute & Train

Improve Accuracy: Annotate your PDFs with Label Studio and retrain models.

Add New Formats: Fork and extend the pipeline for custom documents (e.g., receipts).

```bash
python -m src.cli --input "./tests/data/simple.pdf" --output "./tests/out"
```

## License

MIT © 2024 Moffat Kagiri
