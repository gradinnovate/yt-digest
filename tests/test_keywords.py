import os
import pytest
from datetime import datetime, timedelta
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

# Load environment variables from .env file
env_path = project_root / '.env'
load_dotenv(env_path)

from lib.region import Region
from lib.keywords.google_trends import GoogleTrendsFetcher
from lib.keywords.youtube_trending import YouTubeTrendingFetcher

class TestKeywordsFetchers:
    @pytest.fixture(scope="class")
    def setup_credentials(self):
        """Load API credentials from .env file"""
        # Check if .env file exists
        if not os.path.exists(env_path):
            print(f"\nWarning: .env file not found at {env_path}")
            print("Please create .env file from .env.example template")
        
        credentials = {
            'youtube_api_key': os.getenv('YOUTUBE_API_KEY')
        }
        
        # Log missing credentials
        if not credentials['youtube_api_key']:
            print("\nMissing credentials in .env file:")
            print("- YOUTUBE_API_KEY")
        
        return credentials
    
    @pytest.fixture(scope="class")
    def regions(self):
        """Test regions"""
        return [
            Region.TAIWAN,
            Region.HONG_KONG,
            Region.JAPAN,
            Region.KOREA,
            Region.USA,
            Region.SINGAPORE
        ]
    
    def test_google_trends(self, regions):
        """Test Google Trends fetcher"""
        for region in regions:
            print(f"\nTesting Google Trends for {region}")
            fetcher = GoogleTrendsFetcher(region)
            
            # Test current trends
            results = fetcher.fetch(limit=5)
            self._validate_and_print_results("Google Trends", results, region)
            
            # Test historical trends
            start_time = datetime.now() - timedelta(days=7)
            historical = fetcher.fetch_with_time(start_time, limit=5)
            self._validate_and_print_results("Google Trends (Historical)", historical, region)
    
    def test_youtube_trending(self, setup_credentials, regions):
        """Test YouTube Trending fetcher"""
        api_key = setup_credentials['youtube_api_key']
        if not api_key:
            pytest.skip("YouTube API key not found in .env file")
        
        for region in regions:
            print(f"\nTesting YouTube Trending for {region}")
            fetcher = YouTubeTrendingFetcher(region, api_key=api_key)
            
            results = fetcher.fetch(limit=5)
            self._validate_and_print_results("YouTube Trending", results, region)
    
    def _validate_and_print_results(self, platform: str, results: list, region: Region):
        """Validate and print fetched results"""
        assert isinstance(results, list)
        if results:
            print(f"\n{platform} Results for {region}:")
            print("-" * 50)
            for item in results:
                assert isinstance(item, dict)
                assert 'keyword' in item
                assert 'rank' in item
                
                print(f"#{item['rank']} {item['keyword']}")
                if item.get('score'):
                    print(f"Score: {item['score']}")
                if 'metadata' in item:
                    print("Metadata:")
                    for key, value in item['metadata'].items():
                        print(f"  {key}: {value}")
                print("-" * 30)
        else:
            print(f"No results found for {platform} in {region}")

def main():
    """Run tests with proper output capture"""
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    # Check if python-dotenv is installed
    try:
        import dotenv
    except ImportError:
        print("Error: python-dotenv package is required")
        print("Install it using: pip install python-dotenv")
        sys.exit(1)
    
    pytest.main([__file__, "-v", "--capture=no"])

if __name__ == "__main__":
    main() 