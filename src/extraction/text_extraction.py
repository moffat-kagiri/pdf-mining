import pytesseract
import easyocr
import cv2
from ..utils.config_loader import load_config

config = load_config()
pytesseract.pytesseract.tesseract_cmd = config["paths"]["tesseract_path"]
easyocr_reader = easyocr.Reader(['en'])  # Initialize once

def extract_text(image, engine="auto"):
    img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    if engine == "auto":
        try:
            # First try Tesseract
            text = pytesseract.image_to_string(img_array)
            if len(text.strip()) > 10:  # Minimum character threshold
                return "tesseract", text
        except:
            pass
        
        # Fallback to EasyOCR
        try:
            results = easyocr_reader.readtext(img_array)
            return "easyocr", " ".join([res[1] for res in results])
        except:
            return "failed", ""
        
_reader = None

def get_easyocr_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['en'])
    return _reader
