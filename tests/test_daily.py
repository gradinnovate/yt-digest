import pytest
import logging
from pathlib import Path
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import yaml
from bson.objectid import ObjectId

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from db.keywords import KeywordsDB
from db.videos import VideosDB
from db.transcripts import TranscriptsDB
from lib.youtube.yt_search import YouTubeSearcher
from lib.youtube.downloader import YouTubeDownloader
from lib.ffmpeg.extractor import FFmpegExtractor
from lib.transcript.transcriber import Transcriber
from util.fmt_parser import parse_duration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestDailyWorkflow:
    @pytest.fixture(scope="class")
    def config(self):
        """Load configuration from config.yaml"""
        config_path = project_root / 'config.yaml'
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    @pytest.fixture(scope="class")
    def db_instances(self):
        """Initialize database instances"""
        return {
            'keywords': KeywordsDB(),
            'videos': VideosDB(),
            'transcripts': TranscriptsDB()
        }
    
    @pytest.fixture(scope="class")
    def yt_searcher(self):
        """Initialize YouTube searcher"""
        return YouTubeSearcher()
    
    @pytest.fixture(scope="class")
    def yt_downloader(self, config):
        """Initialize YouTube downloader"""
        download_config = config['youtube']['download']
        return YouTubeDownloader(self.config())
        
    @pytest.fixture(scope="class")
    def audio_extractor(self):
        """Initialize audio extractor"""
        return FFmpegExtractor()
    
    @pytest.fixture(scope="class")
    def transcriber(self):
        """Initialize transcriber"""
        return Transcriber()

    @pytest.fixture(scope="class")
    def keyword_ids(self, db_instances):
        """Fixture to get keyword IDs"""
        try:
            # Mock data
            mock_keywords = [
                {
                    'keyword': 'python programming',
                    'rank': 1,
                    'score': 100,
                    'platform': 'google_trends',
                    'region': 'US',
                    'metadata': {'type': 'trending'}  # Move type to metadata
                },
                {
                    'keyword': 'machine learning',
                    'rank': 2,
                    'score': 90,
                    'platform': 'google_trends',
                    'region': 'US',
                    'metadata': {'type': 'trending'}  # Move type to metadata
                }
            ]
            
            # Insert keywords into database
            keywords_db = db_instances['keywords']
            keyword_ids = []
            for kw in mock_keywords:
                keyword_id = keywords_db.insert_keyword(**kw)
                keyword_ids.append(keyword_id)
                logger.info(f"Inserted keyword: {kw['keyword']}")
            
            assert len(keyword_ids) == len(mock_keywords)
            return keyword_ids
            
        except Exception as e:
            logger.error(f"Error fetching trending keywords: {e}")
            raise

    @pytest.fixture(scope="class")
    def video_ids(self, db_instances, yt_searcher, keyword_ids):
        """Fixture to get video IDs"""
        try:
            videos_db = db_instances['videos']
            keywords_db = db_instances['keywords']
            video_ids = []
            
            for keyword_id in keyword_ids:
                # Get keyword data
                keyword_data = keywords_db.find_one({'_id': ObjectId(keyword_id)})
                if not keyword_data:
                    logger.error(f"Keyword not found for ID: {keyword_id}")
                    continue
                
                # Search videos
                videos = yt_searcher.search(
                    query=keyword_data['keyword'],
                    max_results=3,
                    published_after=datetime.now() - timedelta(days=7),
                    region_code=keyword_data['region']
                )
                
                # Insert videos into database
                for video in videos:
                    video_data = {
                        'keyword_id': keyword_id,
                        'video_id': video['video_id'],
                        'title': video['title'],
                        'url': video['url'],
                        'category': 'education',
                        'thumbnail_url': video['thumbnail_url'],
                        'duration': parse_duration(video['duration']),
                        'views': video['view_count'],
                        'likes': video['like_count'],
                        'language': 'en',
                        'comments': video['comment_count']
                    }
                    video_id = videos_db.insert_video(**video_data)
                    video_ids.append(video_id)
                    logger.info(f"Inserted video: {video['title']}")
            
            assert len(video_ids) > 0, "No videos were found and inserted"
            return video_ids
            
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            raise

    def test_fetch_trending_keywords(self, keyword_ids):
        """Test fetching trending keywords"""
        assert len(keyword_ids) > 0
        logger.info(f"Found {len(keyword_ids)} keywords")

    def test_search_videos(self, video_ids):
        """Test searching videos for each keyword"""
        assert len(video_ids) > 0
        logger.info(f"Found {len(video_ids)} videos")

    @pytest.fixture(scope="class")
    def downloaded_paths(self, db_instances, yt_downloader, video_ids):
        """Fixture to get downloaded video paths"""
        try:
            videos_db = db_instances['videos']
            paths = []
            
            for video_id in video_ids:
                video_data = videos_db.find_one({'_id': video_id})
                
                # Download video
                output_path = yt_downloader.download(
                    url=video_data['url']
                )
                paths.append(output_path)
                logger.info(f"Downloaded video to: {output_path}")
            
            assert len(paths) == len(video_ids)
            return paths
            
        except Exception as e:
            logger.error(f"Error downloading videos: {e}")
            raise

    def test_download_videos(self, downloaded_paths):
        """Test downloading videos"""
        assert len(downloaded_paths) > 0
        for path in downloaded_paths:
            assert path.exists()

    def test_transcribe_videos(self, db_instances, audio_extractor, transcriber, video_ids, downloaded_paths):
        """Test transcribing videos"""
        try:
            transcripts_db = db_instances['transcripts']
            
            for video_id, video_path in zip(video_ids, downloaded_paths):
                # Extract audio using ffmpeg extractor
                audio_path = video_path.with_suffix('.mp3')
                audio_extractor.extract_audio(
                    input_file=str(video_path),
                    output_file=str(audio_path),
                    sample_rate=16000,
                    channels=1
                )
                
                # Transcribe audio
                transcript = transcriber.transcribe(
                    audio_file=str(audio_path),
                    language='en'
                )
                
                # Insert transcript into database
                transcript_data = {
                    'video_id': video_id,
                    'transcript': transcript,
                    'language': 'en'
                }
                transcript_id = transcripts_db.insert_transcript(**transcript_data)
                logger.info(f"Inserted transcript for video: {video_id}")
                
                # Clean up audio file
                audio_path.unlink()
            
        except Exception as e:
            logger.error(f"Error transcribing videos: {e}")
            raise

    def test_full_workflow(self, keyword_ids, video_ids, downloaded_paths, db_instances, transcriber, audio_extractor):
        """Test the complete daily workflow"""
        try:
            # 1. Verify keywords
            self.test_fetch_trending_keywords(keyword_ids)
            
            # 2. Verify videos
            self.test_search_videos(video_ids)
            
            # 3. Verify downloads
            self.test_download_videos(downloaded_paths)
            
            # 4. Transcribe videos
            self.test_transcribe_videos(db_instances, audio_extractor, transcriber, video_ids, downloaded_paths)
            
            logger.info("Daily workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily workflow: {e}")
            raise

def main():
    """Run tests with proper output capture"""
    pytest.main([__file__, "-v", "--capture=no"])

if __name__ == "__main__":
    main() 