# Create a test script test_extractor.py
from src.extraction.text_extraction import TextExtractor
extractor = TextExtractor({"min_text_length": 50})
result = extractor.extract("./tests/data/simple.pdf")
print(result[:500])  # Print first 500 chars