import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseDB

logger = logging.getLogger(__name__)

class KeywordsDB(BaseDB):
    def __init__(self):
        super().__init__('keywords')
        self.logger = logger
    
    def insert_keyword(self, 
                      keyword: str,
                      rank: int,
                      score: int,
                      platform: str,
                      region: str,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Insert a keyword into the database
        
        Args:
            keyword: The keyword text
            rank: Ranking position
            score: Trending score/volume
            platform: Source platform (e.g. google_trends, youtube_trending)
            region: Region code (e.g. TW, JP)
            metadata: Additional metadata
            
        Returns:
            Inserted document ID
        """
        # Type validation
        if not isinstance(keyword, str):
            self.logger.error(f"keyword must be string, got {type(keyword)}")
            raise TypeError(f"keyword must be string, got {type(keyword)}")
        if not isinstance(rank, int):
            self.logger.error(f"rank must be int, got {type(rank)}")
            raise TypeError(f"rank must be int, got {type(rank)}")
        if not isinstance(score, int):
            self.logger.error(f"score must be int, got {type(score)}")
            raise TypeError(f"score must be int, got {type(score)}")
        if not isinstance(platform, str):
            self.logger.error(f"platform must be string, got {type(platform)}")
            raise TypeError(f"platform must be string, got {type(platform)}")
        if not isinstance(region, str):
            self.logger.error(f"region must be string, got {type(region)}")
            raise TypeError(f"region must be string, got {type(region)}")
        if metadata is not None and not isinstance(metadata, dict):
            self.logger.error(f"metadata must be dict, got {type(metadata)}")
            raise TypeError(f"metadata must be dict, got {type(metadata)}")

        #self.logger.debug(f"Inserting keyword: {keyword} with rank {rank}")
        
        now = datetime.now()
        
        # Prepare document
        doc = {
            'keyword': keyword,
            'rank': rank,
            'score': score,
            'platform': platform,
            'region': region,
            'metadata': metadata or {},
            'created_at': now,
            'updated_at': now
        }
        
        # Insert document
        try:
            result = self.insert_one(doc)
            self.logger.debug(f"Successfully inserted keyword: {keyword}")
            return str(result)
        except Exception as e:
            self.logger.error(f"Failed to insert keyword: {e}")
            raise
    
    def find_by_platform_region(self, platform: str, region: str) -> List[Dict[str, Any]]:
        """Find keywords by platform and region"""
        return list(self.find({
            'platform': platform,
            'region': region
        }).sort('rank', 1)) 
    
    