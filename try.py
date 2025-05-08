# Test script test_integration.py
from src.extraction.text_extraction import TextExtractor
from src.utils.config_loader import load_config

config = load_config()  # Your existing config loader
extractor = TextExtractor(config)

# Test with your sample PDF
result = extractor.extract_text("./tests/data/simple.pdf")
print(f"Extracted {len(result)} characters" if result else "Extraction failed")