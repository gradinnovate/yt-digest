from typing import Dict, Any, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
import logging

class BaseDB:
    def __init__(self, collection_name: str):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['yt_digest']
        self.collection: Collection = self.db[collection_name]
        self.logger = logging.getLogger(self.__class__.__name__)

    def insert_one(self, data: Dict[str, Any]) -> str:
        """Insert one document and return its ID"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching the query"""
        return self.collection.find_one(query)

    def update_one(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """Update one document matching the query"""
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            query,
            {'$set': update_data}
        )
        return result.modified_count > 0 
    
    def find_by_id(self, id: str) -> Dict[str, Any]:
        """Find keyword by ID"""
        id = ObjectId(id)
        return self.find_one({'_id': id})