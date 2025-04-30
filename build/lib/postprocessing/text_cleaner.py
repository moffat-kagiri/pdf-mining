import re
from typing import List

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text by removing unwanted characters and normalizing spacing.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        return text.strip()
    
    @staticmethod
    def clean_list(text_list: List[str]) -> List[str]:
        """
        Clean a list of text strings.
        
        Args:
            text_list (List[str]): List of text strings to clean
            
        Returns:
            List[str]: List of cleaned text strings
        """
        return [TextCleaner.clean_text(text) for text in text_list if text.strip()]
    
    @staticmethod
    def remove_empty_lines(text: str) -> str:
        """
        Remove empty lines from text.
        
        Args:
            text (str): Text to process
            
        Returns:
            str: Text with empty lines removed
        """
        lines = text.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)