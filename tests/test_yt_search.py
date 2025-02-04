import os
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import logging

# 設置日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to Python path
project_root = Path(__file__).parent.parent
import sys
sys.path.append(str(project_root))

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

from lib.youtube.yt_search import YouTubeSearcher
from lib.region import Region

class TestYouTubeSearcher:
    @pytest.fixture(scope="class")
    def setup_credentials(self):
        """Load API credentials from .env file"""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            pytest.skip("YouTube API key not found in .env file")
        return api_key
    
    @pytest.fixture(scope="class")
    def searcher(self, setup_credentials):
        """Initialize YouTubeSearcher instance"""
        return YouTubeSearcher(api_key=setup_credentials)
    
    def test_search_videos(self, searcher):
        """Test basic video search functionality"""
        query = "python programming"
        results = searcher.search(
            query=query,
            max_results=5,
            region_code="US"
        )
        
        assert isinstance(results, list)
        if results:
            print(f"\nSearch Results for '{query}':")
            print("-" * 50)
            for video in results:
                assert isinstance(video, dict)
                assert 'video_id' in video
                assert 'title' in video
                assert 'view_count' in video
                
                print(f"Title: {video['title']}")
                print(f"Views: {video['view_count']:,}")
                print(f"URL: {video['url']}")
                print(f"Thumbnail: {video['thumbnail']['url']}")
                print("-" * 30)
    
    def test_search_with_filters(self, searcher):
        """Test search with additional filters"""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        results = searcher.search(
            query="news",
            max_results=3,
            published_after=yesterday,
            region_code="US",
            video_duration="medium"
        )
        
        assert isinstance(results, list)
        if results:
            print("\nRecent News Videos:")
            print("-" * 50)
            for video in results:
                published = datetime.fromisoformat(video['published_at'].rstrip('Z')).replace(tzinfo=timezone.utc)
                assert published > yesterday
                
                print(f"Title: {video['title']}")
                print(f"Published: {published}")
                print(f"Duration: {video['duration']}")
                print("-" * 30)
    
    def test_search_channels(self, searcher):
        """Test channel search functionality"""
        results = searcher.search_channels(
            query="tech news",
            max_results=3,
            region_code="US"
        )
        
        assert isinstance(results, list)
        if results:
            print("\nTech News Channels:")
            print("-" * 50)
            for channel in results:
                assert isinstance(channel, dict)
                assert 'channel_id' in channel
                assert 'title' in channel
                assert 'subscriber_count' in channel
                
                print(f"Channel: {channel['title']}")
                print(f"Subscribers: {channel['subscriber_count']:,}")
                print(f"Videos: {channel['video_count']}")
                print(f"URL: {channel['url']}")
                print(f"Thumbnail: {channel['thumbnail_url']}")
                print("-" * 30)

def main():
    """Run tests with proper output capture"""
    pytest.main([__file__, "-v", "--capture=no"])

if __name__ == "__main__":
    main() 