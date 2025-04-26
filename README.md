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

## Quick Start

```bash
pip install -r requirements.txt  
python extract.py --input statement.pdf --output data.xlsx
```

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
python train.py --dataset your_data/ --epochs 20
```

## License

MIT © 2024 Moffat Kagiri
