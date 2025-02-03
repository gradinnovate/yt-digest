from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import pandas as pd
import time
from .base import KeywordsFetcher
from ..region import Region

class GoogleTrendsFetcher(KeywordsFetcher):
    def __init__(self, region: str | Region = Region.TAIWAN):
        super().__init__(region)
        # 移除 timeout 設置，只保留其他請求參數
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10,30),
            requests_args={
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
                },
                'verify': True
            }
        )
        self.country_code = self._convert_region_code(self.region.get_google_code())
        self.logger.info(f"Initialized GoogleTrendsFetcher for region: {self.region} (country_code: {self.country_code})")
    
    def _convert_region_code(self, code: str) -> str:
        """Convert region code to pytrends format"""
        code_mapping = {
            'TW': 'taiwan',
            'HK': 'hong_kong',
            'JP': 'japan',
            'KR': 'south_korea',
            'US': 'united_states',
            'SG': 'singapore',
            'WORLDWIDE': 'united_states'  # 如果沒有指定地區，使用 US
        }
        result = code_mapping.get(code.upper(), code.lower())
        self.logger.debug(f"Converting region code {code} to {result}")
        return result
    
    def fetch(self, limit: int = 10) -> List[Dict[str, any]]:
        """Fetch current trending searches from Google Trends"""
        try:
            self.logger.info(f"Fetching trends for {self.country_code}")
            
            # 直接獲取熱門搜尋，不需要先建立 payload
            self.logger.debug("Requesting trending searches...")
            trending = self.pytrends.trending_searches(
                pn=self.country_code
            )
            
            self.logger.debug(f"Received response type: {type(trending)}")
            self.logger.debug(f"Response content: {trending}")
            
            if trending is None:
                self.logger.warning("Received None response from Google Trends")
                return []
            
            # 轉換為列表格式
            if isinstance(trending, pd.DataFrame):
                trending = trending.values.flatten().tolist()
            elif isinstance(trending, pd.Series):
                trending = trending.tolist()
            elif not isinstance(trending, list):
                trending = list(trending)
            
            self.logger.info(f"Found {len(trending)} trending searches")
            
            results = []
            for rank, keyword in enumerate(trending[:limit], 1):
                if not isinstance(keyword, str):
                    self.logger.warning(f"Skipping non-string keyword: {keyword}")
                    continue
                
                clean_keyword = self.clean_keyword(keyword)
                if not clean_keyword:
                    self.logger.warning(f"Skipping empty keyword after cleaning: {keyword}")
                    continue
                
                results.append({
                    'keyword': clean_keyword,
                    'rank': rank,
                    'score': None,
                    'metadata': {
                        'platform': 'google_trends',
                        'region': str(self.region),
                        'type': 'trending',
                        'timestamp': datetime.now().isoformat()
                    }
                })
            
            self.logger.info(f"Returning {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch Google Trends: {str(e)}", exc_info=True)
            return []
    
    def fetch_with_time(self, 
                       start_time: datetime,
                       end_time: Optional[datetime] = None,
                       limit: int = 10) -> List[Dict[str, any]]:
        """Return current trends with time information"""
        self.logger.info("Historical data not available, returning current trends")
        results = self.fetch(limit)
        
        for item in results:
            item['metadata'].update({
                'start_time': start_time.isoformat(),
                'end_time': (end_time or datetime.now()).isoformat(),
                'type': 'historical'
            })
        
        return results
    
    def _handle_error(self, error: Exception) -> None:
        """Handle API errors with detailed logging"""
        self.logger.error(f"Google Trends API error: {str(error)}", exc_info=True)
        if hasattr(error, 'response'):
            self.logger.error(f"Response status: {error.response.status_code}")
            self.logger.error(f"Response content: {error.response.content}") 