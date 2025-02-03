from abc import ABC, abstractmethod

class ArticleGenerator(ABC):
    def __init__(self, content: dict):
        """
        Initialize with processed content
        content: dict containing video metadata, transcript, and analyzed content
        """
        self.content = content
    
    @abstractmethod
    def generate(self) -> str:
        """
        Generate formatted article content
        Must be implemented by specific formatters
        """
        pass
    
    def get_metadata(self) -> dict:
        """
        Return article metadata
        """
        return {
            'title': self.content.get('title', ''),
            'author': self.content.get('author', ''),
            'date': self.content.get('date', ''),
            'source_url': self.content.get('url', '')
        } 