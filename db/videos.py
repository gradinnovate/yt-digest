from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId
from .base import BaseDB
import logging

logger = logging.getLogger(__name__)

class VideosDB(BaseDB):
    def __init__(self):
        super().__init__('videos')
        self.logger = logger
    
    def insert_video(self,
                    keyword_id: str,
                    video_category: str,
                    video_thumbnail_url: str,
                    video_url: str,
                    video_youtube_id: str,
                    video_title: str,
                    video_duration: int,
                    video_views: int,
                    video_likes: int,
                    video_language: str,
                    video_comments: int) -> str:
        """Insert a video into the database"""
        # Type validation
        if not isinstance(keyword_id, str):
            raise TypeError(f"keyword_id must be string, got {type(keyword_id)}")
        if not isinstance(video_category, str):
            raise TypeError(f"video_category must be string, got {type(video_category)}")
        if not isinstance(video_thumbnail_url, str):
            raise TypeError(f"video_thumbnail_url must be string, got {type(video_thumbnail_url)}")
        if not isinstance(video_url, str):
            raise TypeError(f"video_url must be string, got {type(video_url)}")
        if not isinstance(video_youtube_id, str):
            raise TypeError(f"video_youtube_id must be string, got {type(video_youtube_id)}")
        if not isinstance(video_title, str):
            raise TypeError(f"video_title must be string, got {type(video_title)}")
        if not isinstance(video_duration, int):
            raise TypeError(f"video_duration must be int, got {type(video_duration)}")
        if not isinstance(video_views, int):
            raise TypeError(f"video_views must be int, got {type(video_views)}")
        if not isinstance(video_likes, int):
            raise TypeError(f"video_likes must be int, got {type(video_likes)}")
        if not isinstance(video_language, str):
            raise TypeError(f"video_language must be string, got {type(video_language)}")
        if not isinstance(video_comments, int):
            raise TypeError(f"video_comments must be int, got {type(video_comments)}")

        now = datetime.now()
        
        doc = {
            'keyword_id': ObjectId(keyword_id),  # 轉換為 ObjectId
            'video_category': video_category,
            'video_thumbnail_url': video_thumbnail_url,
            'video_url': video_url,
            'video_youtube_id': video_youtube_id,
            'video_title': video_title,
            'video_duration': video_duration,
            'video_views': video_views,
            'video_likes': video_likes,
            'video_language': video_language,
            'video_comments': video_comments,
            'created_at': now,
            'updated_at': now
        }
        
        try:
            result = self.insert_one(doc)
            self.logger.debug(f"Successfully inserted video: {video_title}")
            return str(result)
        except Exception as e:
            self.logger.error(f"Failed to insert video: {e}")
            raise
    
    def find_by_video_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Find video by video ID"""
        return self.find_one({'video_id': video_id})
    
    def find_by_keyword(self, keyword_id: str) -> List[Dict[str, Any]]:
        """Find all videos for a given keyword"""
        return list(self.collection.find({'keyword_id': ObjectId(keyword_id)})) 