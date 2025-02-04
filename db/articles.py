from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId
from .base import BaseDB
import logging

logger = logging.getLogger(__name__)

class ArticlesDB(BaseDB):
    def __init__(self):
        super().__init__('articles')
        self.logger = logger
    
    def insert_article(self,
                      keyword_id: str,
                      transcript_id: str,
                      video_id: str,
                      article_language: str,
                      title: str,
                      content: str,
                      tags: str,
                      seo_metadata: Dict[str, Any],
                      published: bool = False) -> str:
        """Insert an article into the database
        
        Args:
            keyword_id: Reference to keywords collection
            transcript_id: Reference to transcripts collection
            video_id: Reference to videos collection
            article_language: Language of the article
            title: Article title
            content: Article content
            tags: Article tags
            seo_metadata: SEO metadata
            published: Publication status
            
        Returns:
            Inserted document ID
        """
        # Type validation
        if not isinstance(keyword_id, str):
            self.logger.error(f"keyword_id must be string, got {type(keyword_id)}")
            raise TypeError(f"keyword_id must be string, got {type(keyword_id)}")
        if not isinstance(transcript_id, str):
            self.logger.error(f"transcript_id must be string, got {type(transcript_id)}")
            raise TypeError(f"transcript_id must be string, got {type(transcript_id)}")
        if not isinstance(video_id, str):
            self.logger.error(f"video_id must be string, got {type(video_id)}")
            raise TypeError(f"video_id must be string, got {type(video_id)}")
        if not isinstance(article_language, str):
            self.logger.error(f"article_language must be string, got {type(article_language)}")
            raise TypeError(f"article_language must be string, got {type(article_language)}")
        if not isinstance(title, str):
            self.logger.error(f"title must be string, got {type(title)}")
            raise TypeError(f"title must be string, got {type(title)}")
        if not isinstance(content, str):
            self.logger.error(f"content must be string, got {type(content)}")
            raise TypeError(f"content must be string, got {type(content)}")
        if not isinstance(tags, str):
            self.logger.error(f"tags must be string, got {type(tags)}")
            raise TypeError(f"tags must be string, got {type(tags)}")
        if not isinstance(seo_metadata, dict):
            self.logger.error(f"seo_metadata must be dict, got {type(seo_metadata)}")
            raise TypeError(f"seo_metadata must be dict, got {type(seo_metadata)}")
        if not isinstance(published, bool):
            self.logger.error(f"published must be bool, got {type(published)}")
            raise TypeError(f"published must be bool, got {type(published)}")

        now = datetime.now()
        
        doc = {
            'keyword_id': ObjectId(keyword_id),
            'transcript_id': ObjectId(transcript_id),
            'video_id': ObjectId(video_id),
            'article_language': article_language,
            'title': title,
            'content': content,
            'tags': tags,
            'seo_metadata': seo_metadata,
            'published': published,
            'created_at': now,
            'updated_at': now
        }
        
        try:
            result = self.insert_one(doc)
            self.logger.debug(f"Successfully inserted article: {title}")
            return str(result)
        except Exception as e:
            self.logger.error(f"Failed to insert article: {e}")
            raise
    
    def find_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Find articles by language"""
        return list(self.collection.find({'article_language': language}))
    
    def find_published(self) -> List[Dict[str, Any]]:
        """Find all published articles"""
        return list(self.collection.find({'published': True}))
    
    def update_publish_status(self, article_id: str, published: bool) -> bool:
        """Update article publish status"""
        try:
            result = self.update_one(
                {'_id': ObjectId(article_id)},
                {'published': published}
            )
            return result
        except Exception as e:
            self.logger.error(f"Failed to update article status: {e}")
            return False 