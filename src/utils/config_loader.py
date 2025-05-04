import yaml
from pathlib import Path

def load_config(config_name="default"):
    config_path = Path(__file__).parent.parent / "configs" / f"{config_name}.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Set default paths
    config["paths"]["poppler_path"] = r"C:\Program Files\poppler\Library\bin"
    config["paths"]["tesseract_path"] = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    return config