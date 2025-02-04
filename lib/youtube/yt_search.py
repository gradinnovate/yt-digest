from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeSearcher:
    """YouTube search functionality using YouTube Data API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube API client
        
        Args:
            api_key: YouTube Data API key. If not provided, will try to get from environment
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load environment variables from .env file
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / '.env'
        load_dotenv(env_path)
        
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable or pass to constructor.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def search(self, 
              query: str,
              max_results: int = 10,
              published_after: Optional[datetime] = None,
              region_code: Optional[str] = None,
              relevance_language: Optional[str] = None,
              video_duration: Optional[str] = None) -> List[Dict]:
        """Search YouTube videos
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            published_after: Only include videos published after this time
            region_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB')
            relevance_language: ISO 639-1 language code (e.g. 'en', 'es')
            video_duration: Filter by duration: 'short' (<4 min), 'medium' (4-20 min), 'long' (>20 min)
        
        Returns:
            List of video details dictionaries
        """
        try:
            # Build search request
            search_params = {
                'q': query,
                'part': 'id,snippet',
                'type': 'video',
                'maxResults': min(max_results, 50),
                'fields': 'items(id(videoId),snippet(title,description,publishedAt,channelId,channelTitle,thumbnails))'
            }
            
            # Add optional filters
            if published_after:
                formatted_time = published_after.strftime('%Y-%m-%dT%H:%M:%SZ')
                search_params['publishedAfter'] = formatted_time
            if region_code:
                search_params['regionCode'] = region_code
            if relevance_language:
                search_params['relevanceLanguage'] = relevance_language
            if video_duration:
                search_params['videoDuration'] = video_duration
            
            self.logger.debug(f"Searching with params: {search_params}")
            
            # Execute search request
            search_response = self.youtube.search().list(**search_params).execute()
            
            if not search_response.get('items'):
                self.logger.warning("No videos found")
                return []
            
            # Get video IDs for detailed info
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video information
            videos_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            # Process and format results
            results = []
            for item in videos_response.get('items', []):
                try:
                    # Get video thumbnail URL (default to highest quality available)
                    thumbnails = item['snippet'].get('thumbnails', {})
                    thumbnail_url = None
                    for quality in ['maxres', 'standard', 'high', 'medium', 'default']:
                        if quality in thumbnails:
                            thumbnail_url = thumbnails[quality]['url']
                            break
                    
                    video_data = {
                        'video_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_id': item['snippet']['channelId'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'like_count': int(item['statistics'].get('likeCount', 0)),
                        'comment_count': int(item['statistics'].get('commentCount', 0)),
                        'duration': item['contentDetails']['duration'],
                        'tags': item['snippet'].get('tags', []),
                        'url': f"https://www.youtube.com/watch?v={item['id']}",
                        'thumbnail_url': thumbnail_url,
                        # Add thumbnail details
                        'thumbnail': {
                            'url': thumbnail_url,
                            'width': thumbnails.get(quality, {}).get('width'),
                            'height': thumbnails.get(quality, {}).get('height')
                        } if thumbnail_url else None
                    }
                    results.append(video_data)
                except (KeyError, ValueError) as e:
                    self.logger.warning(f"Error processing video {item.get('id')}: {e}")
                    continue
            
            self.logger.info(f"Found {len(results)} videos")
            return results
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e.resp.status} {e.content}")
            raise
        except Exception as e:
            self.logger.error(f"Error searching YouTube: {e}")
            raise
    
    def search_channels(self,
                       query: str,
                       max_results: int = 10,
                       region_code: Optional[str] = None) -> List[Dict]:
        """Search YouTube channels
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            region_code: ISO 3166-1 alpha-2 country code
            
        Returns:
            List of channel details dictionaries
        """
        try:
            # Build search request
            search_params = {
                'q': query,
                'part': 'id,snippet',
                'type': 'channel',
                'maxResults': min(max_results, 50)
            }
            
            if region_code:
                search_params['regionCode'] = region_code
            
            self.logger.debug(f"Searching channels with params: {search_params}")
            
            # Execute search
            search_response = self.youtube.search().list(**search_params).execute()
            
            if not search_response.get('items'):
                self.logger.warning("No channels found")
                return []
            
            # Get channel IDs
            channel_ids = [item['id']['channelId'] for item in search_response['items']]
            
            # Get detailed channel information
            channels_response = self.youtube.channels().list(
                part='snippet,statistics',
                id=','.join(channel_ids)
            ).execute()
            
            # Process results
            results = []
            for item in channels_response.get('items', []):
                try:
                    # Get the best quality thumbnail URL
                    thumbnails = item['snippet'].get('thumbnails', {})
                    thumbnail_url = None
                    for quality in ['high', 'medium', 'default']:
                        if quality in thumbnails:
                            thumbnail_url = thumbnails[quality]['url']
                            break
                    
                    channel_data = {
                        'channel_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                        'video_count': int(item['statistics'].get('videoCount', 0)),
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'url': f"https://www.youtube.com/channel/{item['id']}",
                        'thumbnail_url': thumbnail_url
                    }
                    results.append(channel_data)
                except (KeyError, ValueError) as e:
                    self.logger.warning(f"Error processing channel {item.get('id')}: {e}")
                    continue
            
            self.logger.info(f"Found {len(results)} channels")
            return results
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e.resp.status} {e.content}")
            raise
        except Exception as e:
            self.logger.error(f"Error searching YouTube channels: {e}")
            raise
