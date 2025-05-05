import yaml
from pathlib import Path

def load_config(config_name="default"):
    # Only look in root config folder
    root_dir = Path(__file__).parent.parent.parent
    config_path = root_dir / "config" / f"{config_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file '{config_name}.yaml' not found at:\n"
            f"- {config_path}\n"
            "Please ensure the config file exists in the root config directory."
        )

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Set default paths 
        config.setdefault("paths", {})
        config["paths"]["poppler_path"] = r"C:\Program Files\poppler\Library\bin"
        config["paths"]["tesseract_path"] = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        return config
    
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file {config_path}: {str(e)}")