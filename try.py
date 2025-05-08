from src.extraction.text_extraction import TextExtractor
from src.utils.config_loader import load_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_processing(pdf_path: str):
    """Enhanced test function with proper error handling"""
    try:
        config = load_config()
        extractor = TextExtractor(config)
        
        logger.info(f"\n{'='*40}\nTesting file: {pdf_path}\n{'='*40}")
        
        result = extractor.extract_text(pdf_path)
        
        if not result:
            logger.error("Extraction completely failed")
            return
            
        # Successful extraction metrics
        logger.info(f"Extracted {len(result)} characters")
        logger.info("=== SAMPLE TEXT ===")
        logger.info(result[:500] + "...")
        
        # Quality metrics
        lines = result.splitlines()
        words = result.split()
        logger.info("\n=== QUALITY REPORT ===")
        logger.info(f"Lines: {len(lines)}")
        logger.info(f"Words: {len(words)}")
        logger.info(f"Avg words/line: {len(words)/max(1,len(lines)):.1f}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Test failed: {str(e)}")
        return None

# Add to your test script
def calculate_quality_score(text):
    lines = text.splitlines()
    words = text.split()
    return {
        'char_count': len(text),
        'word_count': len(words),
        'line_count': len(lines),
        'words_per_line': round(len(words)/len(lines), 1),
        'bullet_points': text.count('•')
    }

if __name__ == "__main__":
    # Test both PDF types
    test_pdf_processing("./tests/data/simple.pdf")  # Text-based
    test_pdf_processing("./tests/data/image.pdf")   # Image-based