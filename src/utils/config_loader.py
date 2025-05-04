import yaml
import logging
from pathlib import Path

DEFAULT_CONFIG = {
    "dpi": 200,
    "temp_dir": "./temp",
    "poppler_path": r"C:\Program Files\poppler\Library\bin",
    "output_format": "xlsx",
    "ocr": {
        "engine": "tesseract",
        "lang": "eng",
        "config": "--oem 3 --psm 6"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(levelname)s - %(message)s"
    }
}

def load_config(file_path=None):
    """Load configuration from file or return default config."""
    if file_path is None:
        logging.info("No config file provided, using default configuration")
        return DEFAULT_CONFIG
    
    try:
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
            return {**DEFAULT_CONFIG, **(config or {})}  # Merge with defaults
    except Exception as e:
        logging.warning(f"Failed to load config from {file_path}: {str(e)}")
        return DEFAULT_CONFIG

def load_ocr_config() -> dict:
    """Load OCR configuration from YAML file."""
    config_path = Path(__file__).parents[2] / "configs" / "ocr_config.yaml"
    return load_config(str(config_path))

