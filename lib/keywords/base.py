from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import logging
from ..region import Region  # Add this import

class KeywordsFetcher(ABC):
    """Base class for fetching trending keywords from different platforms"""
    
    def __init__(self, region: str | Region = Region.TAIWAN):
        """
        Initialize keywords fetcher
        
        Args:
            region: Region code or Region enum (default: Region.TAIWAN)
        """
        self.region = region if isinstance(region, Region) else Region.from_code(region)
        if not self.region:
            raise ValueError(f"Invalid region code: {region}")
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def fetch(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        Fetch trending keywords
        
        Args:
            limit: Maximum number of keywords to fetch
            
        Returns:
            List of keyword dictionaries containing:
            - keyword: The trending keyword/topic
            - rank: Ranking position
            - score: Trending score/volume (if available)
            - metadata: Additional platform-specific data
        """
        pass
    
    @abstractmethod
    def fetch_with_time(self, 
                       start_time: datetime,
                       end_time: Optional[datetime] = None,
                       limit: int = 10) -> List[Dict[str, any]]:
        """
        Fetch trending keywords within a time range
        
        Args:
            start_time: Start time for the trend data
            end_time: End time (default: current time)
            limit: Maximum number of keywords to fetch
            
        Returns:
            List of keyword dictionaries with timestamp information
        """
        pass
    
    def clean_keyword(self, keyword: str) -> str:
        """Clean and normalize keyword text"""
        return keyword.strip()
    
    def validate_result(self, result: List[Dict[str, any]]) -> bool:
        """
        Validate fetched results
        
        Args:
            result: List of keyword dictionaries
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(result, list):
            return False
            
        for item in result:
            if not isinstance(item, dict):
                return False
            if 'keyword' not in item or 'rank' not in item:
                return False
                
        return True 