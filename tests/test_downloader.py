import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from lib.youtube.downloader import YouTubeDownloader

def test_download():
    # Initialize downloader with config
    config_path = os.path.join(project_root, "config.yaml")
    downloader = YouTubeDownloader(config_path)
    
    # Test URL
    url = "https://www.youtube.com/watch?v=pmljvWUrm0I"
    
    try:
        # Test video download
        print("Testing video download...")
        result = downloader.download_video(url)
        
        print("\nDownload Results:")
        print(f"Video path: {result['video']}")
        print(f"Title: {result['title']}")
        print(f"Duration: {result['duration']} seconds")
        print("\nSubtitles:")
        for lang, path in result['subtitles'].items():
            print(f"- {lang}: {path}")
            
        # Verify files exist
        assert os.path.exists(result['video']), "Video file not found!"
        for sub_path in result['subtitles'].values():
            assert os.path.exists(sub_path), f"Subtitle file not found: {sub_path}"
            
        print("\nAll files downloaded successfully!")
        
    except Exception as e:
        print(f"\nError during download: {str(e)}")
        raise

if __name__ == "__main__":
    test_download() 