from typing import List, Dict, Optional
from datetime import datetime
import tweepy
from .base import KeywordsFetcher
from ..region import Region

class TwitterTrendingFetcher(KeywordsFetcher):
    def __init__(self, 
                 region: str = "TW",
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 access_token: Optional[str] = None,
                 access_token_secret: Optional[str] = None):
        super().__init__(region)
        
        if all([api_key, api_secret, access_token, access_token_secret]):
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(auth)
        else:
            self.api = None
            self.logger.warning("Twitter API credentials not provided")
    
    def fetch(self, limit: int = 10) -> List[Dict[str, any]]:
        """Fetch current trending topics from Twitter"""
        if not self.api:
            return []
            
        try:
            # Get WOEID for region directly from Region enum
            woeid = self.region.get_twitter_woeid()
            
            # Get trending topics
            trends = self.api.get_place_trends(woeid)
            
            results = []
            for rank, trend in enumerate(trends[0]['trends'][:limit], 1):
                results.append({
                    'keyword': self.clean_keyword(trend['name']),
                    'rank': rank,
                    'score': trend['tweet_volume'],
                    'metadata': {
                        'platform': 'twitter',
                        'region': self.region,
                        'tweet_volume': trend['tweet_volume'],
                        'query': trend['query']
                    }
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch Twitter trends: {str(e)}")
            return []
    
    def fetch_with_time(self, 
                       start_time: datetime,
                       end_time: Optional[datetime] = None,
                       limit: int = 10) -> List[Dict[str, any]]:
        """
        Note: Twitter API doesn't provide historical trending data
        This will return current trending topics
        """
        return self.fetch(limit) 