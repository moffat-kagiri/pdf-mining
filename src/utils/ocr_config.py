import pytesseract

# Point to the Tesseract executable installed by Chocolatey
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_tesseract_languages():
    return pytesseract.get_languages(config='')