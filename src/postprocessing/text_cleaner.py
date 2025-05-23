import re
from typing import Dict, List, Any

class TextCleaner:
    def __init__(self, config: dict):
        self.replace_patterns = config.get('replace_patterns', [])
        self.common_errors = {
            r'(\w+)@(\w+)-com': r'\1@\2.com',
            r'Neugi': 'Ngugi',
            r'[oO0¢]\s': '• '
        }

    def clean(self, text: str) -> str:
        """Multi-stage text cleaning"""
        # Standardize line endings
        text = text.replace('\r\n', '\n')
        
        # Apply configured replacements
        for pattern, replacement in self.replace_patterns:
            text = re.sub(pattern, replacement, text)
            
        # Fix common OCR errors
        for error, fix in self.common_errors.items():
            text = re.sub(error, fix, text)
            
        return text.strip()

    def clean_text(text: str) -> str:
        """Clean while preserving meaningful newlines"""
        # Preserve multiple newlines between paragraphs
        text = re.sub(r'(\n\s*){3,}', '\n\n', text.strip())
        
        # Normalize single newlines
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # Fix bullet points
        text = re.sub(r'([•▪♦➢])\s+', r'\n\1 ', text)
        
        return text

    def clean_ocr_text(text: str) -> str:
        """Fix common OCR artifacts"""
        # Email fixes
        text = re.sub(r'(\w+)@(\w+)-com', r'\1@\2.com', text)
        
        # Name corrections
        text = text.replace("Neugi", "Ngugi")
        
        # Bullet point standardization
        text = re.sub(r'[oO0]\s', '• ', text)
        
        # Date format normalization
        text = re.sub(r'(\d{4})\s*—\s*(\w+)', r'\1-\2', text)
        
        # Remove isolated characters
        return re.sub(r'\s\w\s', ' ', text)
    def process_pymupdf_output(layout: Dict[str, Any]) -> List[Dict[str, str]]:
        """Process text blocks from PyMuPDF layout."""
        results = []
        if not layout:
            return results
            
        for block in layout.get('blocks', []):
            text = clean_text(block.get('text', ''))
            if text:
                results.append({
                    'text': text,
                    'type': block.get('type', 'unknown'),
                    'bbox': block.get('bbox', []),
                    'confidence': block.get('confidence', 1.0)
                })
        return results

    def process_donut_output(image, predictions) -> List[Dict[str, str]]:
        """Process text predictions from Donut model."""
        results = []
        if not predictions:
            return results
            
        for pred in predictions:
            text = clean_text(pred.get('text', ''))
            if text:
                results.append({
                    'text': text,
                    'type': pred.get('label', 'text'),
                    'bbox': pred.get('box', []),
                    'confidence': pred.get('score', 0.0)
                })
        return results