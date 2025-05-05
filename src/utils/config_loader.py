# src/utils/config_loader.py
import yaml
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "paths": {
        "poppler_path": r"C:\Program Files\poppler-25.04.0\Library\bin",
        "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        "output_dir": "output"
    },
    "ocr": {
        "default_engine": "tesseract",
        "fallback_engine": "easyocr",
        "languages": ["eng"]
    },
    "logging": {
        "level": "INFO",
        "file": "pdf_mining.log"
    }
}

def load_config(config_name="default"):
    """Load configuration with fallback to defaults"""
    config_dir = Path(__file__).parent.parent / "configs"
    config_path = config_dir / f"{config_name}.yaml"
    
    try:
        # Create config directory if missing
        config_dir.mkdir(exist_ok=True)
        
        # Load or create config file
        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
        else:
            with open(config_path, 'w') as f:
                yaml.dump(DEFAULT_CONFIG, f)
            user_config = {}
            
        # Merge with defaults
        config = {**DEFAULT_CONFIG, **user_config}
        
        # Convert paths to raw strings for Windows
        for path_key in ["poppler_path", "tesseract_path"]:
            if path_key in config["paths"]:
                config["paths"][path_key] = str(Path(config["paths"][path_key]))
        
        return config
    
    except Exception as e:
        logger.error(f"Config load failed: {str(e)}")
        logger.info("Using default configuration")
        return DEFAULT_CONFIG

# Initialize config at module level
config = load_config()