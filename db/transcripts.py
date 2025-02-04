from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId
from .base import BaseDB
import logging

logger = logging.getLogger(__name__)

class TranscriptsDB(BaseDB):
    def __init__(self):
        super().__init__('transcripts')
        self.logger = logger
    
    def insert_transcript(self,
                         video_id: str,
                         transcript: str,
                         language: str) -> str:
        """Insert a transcript into the database
        
        Args:
            video_id: Reference to videos collection
            transcript: Full transcript text
            language: Language of the transcript
            
        Returns:
            Inserted document ID
        """
        # Type validation
        if not isinstance(video_id, str):
            self.logger.error(f"video_id must be string, got {type(video_id)}")
            raise TypeError(f"video_id must be string, got {type(video_id)}")
        if not isinstance(transcript, str):
            self.logger.error(f"transcript must be string, got {type(transcript)}")
            raise TypeError(f"transcript must be string, got {type(transcript)}")
        if not isinstance(language, str):
            self.logger.error(f"language must be string, got {type(language)}")
            raise TypeError(f"language must be string, got {type(language)}")

        now = datetime.now()
        
        doc = {
            'video_id': ObjectId(video_id),  # 轉換為 ObjectId
            'transcript': transcript,
            'language': language,
            'created_at': now,
            'updated_at': now
        }
        
        try:
            result = self.insert_one(doc)
            self.logger.debug(f"Successfully inserted transcript for video: {video_id}")
            return str(result)
        except Exception as e:
            self.logger.error(f"Failed to insert transcript: {e}")
            raise
    
    def find_by_video_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Find transcript by video ID"""
        return self.find_one({'video_id': ObjectId(video_id)})
    
    def find_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Find all transcripts in a specific language"""
        return list(self.collection.find({'language': language})) 