import layoutparser as lp
import pymupdf

def analyze_pdf(pdf_path):
    # Try PyMuPDF first for native PDFs
    try:
        doc = pymupdf.open(pdf_path)
        return [page.get_text("dict") for page in doc]
    except:
        # Fallback to Donut for scanned PDFs
        model = lp.AutoLayoutModel("donut")
        images = convert_pdf(pdf_path)  # From pdf_to_image.py
        return [model.detect(img) for img in images]