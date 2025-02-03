from typing import List, Dict, Optional
from datetime import datetime
import requests
from .base import KeywordsFetcher
from ..region import Region

class YouTubeTrendingFetcher(KeywordsFetcher):
    def __init__(self, region: str = "TW", api_key: Optional[str] = None):
        super().__init__(region)
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def fetch(self, limit: int = 10) -> List[Dict[str, any]]:
        """Fetch trending videos and extract keywords"""
        if not self.api_key:
            self.logger.error("YouTube API key not provided")
            return []
            
        try:
            # Get trending videos
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': self.region.get_youtube_code(),
                'maxResults': limit,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for rank, item in enumerate(data['items'], 1):
                # Extract keywords from title and tags
                keywords = set()
                keywords.add(item['snippet']['title'])
                keywords.update(item['snippet'].get('tags', []))
                
                results.append({
                    'keyword': self.clean_keyword(item['snippet']['title']),
                    'rank': rank,
                    'score': int(item['statistics']['viewCount']),
                    'metadata': {
                        'platform': 'youtube',
                        'region': self.region,
                        'video_id': item['id'],
                        'tags': list(keywords),
                        'view_count': item['statistics']['viewCount'],
                        'like_count': item['statistics'].get('likeCount', 0)
                    }
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch YouTube trends: {str(e)}")
            return []
    
    def fetch_with_time(self, 
                       start_time: datetime,
                       end_time: Optional[datetime] = None,
                       limit: int = 10) -> List[Dict[str, any]]:
        """
        Note: YouTube API doesn't provide historical trending data
        This will return current trending videos
        """
        return self.fetch(limit) 