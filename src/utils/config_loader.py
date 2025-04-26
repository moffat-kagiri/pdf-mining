import yaml
from pathlib import Path

def load_config(file_path: str) -> dict:
    """Load YAML config files."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def load_ocr_config() -> dict:
    """Load OCR configuration from YAML file."""
    config_path = Path(__file__).parents[2] / "configs" / "ocr_config.yaml"
    return load_config(str(config_path))

