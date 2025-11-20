import re

class MarkdownCleaner:
    """Clean and post-process markdown text."""
    
    @staticmethod
    def clean(markdown_text: str) -> str:
        """
        Clean up markdown text.
        
        Args:
            markdown_text: Raw markdown text
            
        Returns:
            str: Cleaned markdown text
        """
        # Remove multiple consecutive newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        # Clean up citations [1] format (ensure proper spacing)
        markdown_text = re.sub(r'\[(\d+)\]', r'[\1]', markdown_text)
        
        return markdown_text.strip()

