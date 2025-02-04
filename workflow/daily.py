import logging
from pathlib import Path
import yaml
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from db.keywords import KeywordsDB
from db.videos import VideosDB
from db.transcripts import TranscriptsDB
from lib.youtube.yt_search import YouTubeSearcher
from lib.youtube.downloader import YouTubeDownloader
from lib.ffmpeg.extractor import FFmpegExtractor
from lib.transcript.transcriber import Transcriber
from lib.keywords.google_trends import GoogleTrendsFetcher
from lib.keywords.youtube_trending import YouTubeTrendingFetcher
from util.fmt_parser import parse_duration
from lib.region import Region


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Get the root logger and set its level
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # Set root logger to WARNING to filter out third-party logs

# Set up module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set up our module loggers
our_modules = [
    'db.keywords', 
    'lib.keywords.google_trends', 
    'lib.keywords.youtube_trending',
    'lib.youtube',
    'lib.ffmpeg',
    'lib.transcript'
]

for name in our_modules:
    module_logger = logging.getLogger(name)
    module_logger.setLevel(logging.DEBUG)
    # Ensure the logger has a handler
    if not module_logger.handlers:
        module_logger.addHandler(logging.StreamHandler(sys.stdout))

# Set third party modules to WARNING or higher
third_party_modules = [
    'pytrends',
    'urllib3',
    'requests',
    'googleapiclient',
    'pytube',
    'moviepy'
]

for name in third_party_modules:
    module_logger = logging.getLogger(name)
    module_logger.setLevel(logging.WARNING)


class DailyWorkflow:
    def __init__(self, config_path: str = 'config.yaml', api_key: str = None):
        """Initialize workflow with configuration"""
        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        # Initialize components
        self.keywords_db = KeywordsDB()
        self.videos_db = VideosDB()
        self.transcripts_db = TranscriptsDB()
        self.yt_searcher = YouTubeSearcher(api_key=api_key)
        self.yt_downloader = YouTubeDownloader(self.config)
        self.audio_extractor = FFmpegExtractor()
        self.transcriber = Transcriber()
        # Initialize keyword fetchers
        self.keyword_fetchers = {
            region: {
                'google_trends': GoogleTrendsFetcher(region),
                #'youtube_trending': YouTubeTrendingFetcher(region, api_key)
            }
            for region in self.config['regions']
        }
    def fetch_trending_keywords(self) -> List[str]:
        """Fetch trending keywords from all sources and regions"""
        keyword_ids = []
        
        # Iterate through each region's fetchers
        for region, fetchers in self.keyword_fetchers.items():
            for platform, fetcher in fetchers.items():
                try:
                    keywords = fetcher.fetch()
                    logger.debug(f"keywords: {keywords}")
                    logger.info(f"Fetched {len(keywords)} keywords from {platform} for {region}")
                    
                    for keyword_data in keywords:
                        logger.debug(f"Processing keyword data: {keyword_data}")
                        
                        # Convert Region enum to string
                        metadata = keyword_data.get('metadata', {})
                        if 'region' in metadata and isinstance(metadata['region'], Region):
                            metadata['region'] = metadata['region'].value
                        
                        # Ensure score is an integer
                        score = keyword_data.get('score')
                        if score is None:
                            score = 0
                        
                        # Ensure all required fields have correct types
                        try:
                            insert_data = {
                                'keyword': str(keyword_data['keyword']),  # Ensure string
                                'rank': int(keyword_data['rank']),       # Ensure int
                                'score': int(score),                     # Ensure int
                                'platform': str(platform),               # Ensure string
                                'region': str(region.value if isinstance(region, Region) else region),  # Ensure string
                                'metadata': dict(metadata or {}),        # Ensure dict
                            }
                            #logger.debug(f"Inserting keyword with data: {insert_data}")
                            
                            keyword_id = self.keywords_db.insert_keyword(**insert_data)
                            keyword_ids.append(keyword_id)
                            logger.info(
                                f"Inserted keyword: {keyword_data['keyword']} "
                                f"(rank: {keyword_data['rank']}, score: {score}, "
                                f"platform: {platform}, region: {region})"
                            )
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid data type in keyword data: {e}")
                            logger.error(f"Problematic data: {keyword_data}")
                            continue
                            
                except Exception as e:
                    logger.error(
                        f"Error fetching keywords for {platform} in {region}: {e}"
                    )
                    continue
        
        if not keyword_ids:
            logger.warning("No keywords were fetched from any source")
            
        return keyword_ids
    
    def search_videos(self, keyword_ids: List[str]) -> List[str]:
        """Search videos for keywords"""
        video_ids = []
        
        for keyword_id in keyword_ids:
            keyword_data = self.keywords_db.find_by_id(keyword_id)
            if not keyword_data:
                continue
                
            videos = self.yt_searcher.search(
                query=keyword_data['keyword'],
                max_results=3,
                published_after=datetime.now() - timedelta(days=7),
                region_code=keyword_data['region']
            )
            
            for video in videos:
                # 修正 video_data 結構以符合 schema
                video_data = {
                    'keyword_id': keyword_id,
                    'video_category': 'education',
                    'video_thumbnail_url': video['thumbnail_url'],
                    'video_url': video['url'],
                    'video_youtube_id': video['video_id'],  # 修正: video_id -> video_youtube_id
                    'video_title': video['title'],
                    'video_duration': parse_duration(video['duration']),
                    'video_views': int(video['view_count']),  # 確保是整數
                    'video_likes': int(video['like_count']),  # 確保是整數
                    'video_language': 'en',
                    'video_comments': int(video['comment_count'])  # 確保是整數
                }
                video_id = self.videos_db.insert_video(**video_data)
                video_ids.append(video_id)
                logger.info(f"Inserted video: {video['title']}")
                
        return video_ids
    
    def download_videos(self, video_ids: List[str]) -> List[Path]:
        """Download videos"""
        path_map = {}
        
        for video_id in video_ids:
            video_data = self.videos_db.find_by_id(video_id)
            if not video_data:
                continue
                
            output_path = self.yt_downloader.download_video(
                url=video_data['video_url'],
                extract_audio=False
            )
            path_map[video_id] = output_path['video']
            logger.info(f"Downloaded video to: {output_path}")
            
        return path_map
    
    def transcribe_videos(self, video_ids: List[str], video_paths: Dict[str, str]):
        """Transcribe downloaded videos"""
        for video_id in video_ids:
            video_path = video_paths.get(video_id)
            if not video_path:
                continue
            
            try:
                # Transcribe video
                transcript = self.transcriber.transcribe(video_path)
                
                # Insert transcript
                self.transcripts_db.insert_transcript(
                    video_id=video_id,
                    transcript=transcript['text'],
                    language=transcript['language']
                )
                
                logger.info(f"Transcribed video {video_id}")
                
            except Exception as e:
                logger.error(f"Failed to transcribe video {video_id}: {e}")
                continue
    
    def run(self):
        """Run the complete workflow"""
        try:
            # 1. Fetch trending keywords
            keyword_ids = self.fetch_trending_keywords()
            logger.info(f"Fetched {len(keyword_ids)} keywords")
            
            # 2. Search videos for keywords
            video_ids = self.search_videos(keyword_ids)
            logger.info(f"Found {len(video_ids)} videos")
            
            # 3. Download videos
            video_paths = self.download_videos(video_ids)
            logger.info(f"Downloaded {len(video_paths)} videos")
            
            # 4. Transcribe videos
            self.transcribe_videos(video_ids, video_paths)
            logger.info("Workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            raise

def main():
    """Main entry point"""
    try:
        config_path = os.path.join(project_root, 'config.yaml')
        env_path = os.path.join(project_root, '.env')
        
        # Load environment variables
        load_dotenv(env_path)
        api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not found")
        print('prepare workflow')     
        workflow = DailyWorkflow(config_path, api_key)
        print('run workflow')
        workflow.run()
    except Exception as e:
        logger.error(f"Failed to run workflow: {e}")
        exit(1)

if __name__ == "__main__":
    main()
