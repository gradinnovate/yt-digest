from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from db.keywords import KeywordsDB
from db.videos import VideosDB
from db.transcripts import TranscriptsDB
from db.articles import ArticlesDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_mongodb():
    """Initialize MongoDB collections and indexes"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        
        # Get or create database
        db_name = 'yt_digest'
        logger.info(f"Available databases: {client.list_database_names()}")
        db = client[db_name]
        logger.info(f"Using database: {db_name}")
        
        # Create collections if they don't exist
        collections = ['keywords', 'videos', 'transcripts', 'articles']
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                logger.info(f"Created collection: {collection}")
            else:
                logger.info(f"Collection exists: {collection}")

        # Initialize DB classes
        keywords_db = KeywordsDB()
        videos_db = VideosDB()
        transcripts_db = TranscriptsDB()
        articles_db = ArticlesDB()


        # Define collection schemas
        db.command({
            'collMod': 'keywords',
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['keyword', 'rank', 'score', 'platform', 'region'],
                    'properties': {
                        'keyword': {'bsonType': 'string'},
                        'rank': {'bsonType': 'int'},
                        'score': {'bsonType': 'int'},
                        'platform': {'bsonType': 'string'},
                        'region': {'bsonType': 'string'},
                        'metadata': {'bsonType': 'object'},
                        'created_at': {'bsonType': 'date'},
                        'updated_at': {'bsonType': 'date'}
                    }
                }
            }
        })

        db.command({
            'collMod': 'videos',
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': [
                        'keyword_id', 'video_category', 'video_thumbnail_url',
                        'video_url', 'video_youtube_id', 'video_title', 'video_duration',
                        'video_views', 'video_likes', 'video_language', 'video_comments'
                    ],
                    'properties': {
                        'keyword_id': {'bsonType': 'objectId'},
                        'video_category': {'bsonType': 'string'},
                        'video_thumbnail_url': {'bsonType': 'string'},
                        'video_url': {'bsonType': 'string'},
                        'video_youtube_id': {'bsonType': 'string'},
                        'video_title': {'bsonType': 'string'},
                        'video_duration': {'bsonType': 'int'},
                        'video_views': {'bsonType': 'int'},
                        'video_likes': {'bsonType': 'int'},
                        'video_language': {'bsonType': 'string'},
                        'video_comments': {'bsonType': 'int'},
                        'created_at': {'bsonType': 'date'},
                        'updated_at': {'bsonType': 'date'}
                    }
                }
            }
        })

        db.command({
            'collMod': 'transcripts',
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['video_id', 'transcript', 'language'],
                    'properties': {
                        'video_id': {'bsonType': 'objectId'},
                        'transcript': {'bsonType': 'string'},
                        'language': {'bsonType': 'string'},
                        'created_at': {'bsonType': 'date'},
                        'updated_at': {'bsonType': 'date'}
                    }
                }
            }
        })

        db.command({
            'collMod': 'articles',
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['keyword_id', 'transcript_id', 'video_id', 'article_language', 'title', 'content', 'tags', 'seo_metadata'],
                    'properties': {
                        'keyword_id': {'bsonType': 'objectId'},
                        'transcript_id': {'bsonType': 'objectId'},
                        'video_id': {'bsonType': 'objectId'},
                        'article_language': {'bsonType': 'string'},
                        'title': {'bsonType': 'string'},
                        'content': {'bsonType': 'string'},
                        'tags': {'bsonType': 'string'},
                        'seo_metadata': {'bsonType': 'object'},
                        'published': {'bsonType': 'bool'},
                        'created_at': {'bsonType': 'date'},
                        'updated_at': {'bsonType': 'date'}
                    }
                }
            }
        })

        logger.info("Database initialization completed successfully")
        return {
            'keywords': keywords_db,
            'videos': videos_db,
            'transcripts': transcripts_db,
            'articles': articles_db
        }

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def print_table_structure():
    """Print MongoDB collections structure based on actual data"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017')
        db = client['yt_digest']
        
        print("\nDatabase Schema:")
        print("================")
        
        for collection_name in db.list_collection_names():
            print(f"\nCollection: {collection_name}")
            print("=" * (len(collection_name) + 11))
            
            # Get collection validator
            collection_info = db.command("listCollections", 
                                      filter={"name": collection_name})
            validator = None
            for info in collection_info['cursor']['firstBatch']:
                if 'options' in info and 'validator' in info['options']:
                    validator = info['options']['validator']
            
            if validator and '$jsonSchema' in validator:
                schema = validator['$jsonSchema']
                
                # Print required fields
                if 'required' in schema:
                    print("\nRequired Fields:")
                    for field in schema['required']:
                        print(f"  - {field}")
                
                # Print field definitions
                if 'properties' in schema:
                    print("\nField Definitions:")
                    for field, props in schema['properties'].items():
                        field_type = props.get('bsonType', 'any')
                        desc = props.get('description', '')
                        required = field in schema.get('required', [])
                        
                        field_info = f"  - {field}: {field_type}"
                        if required:
                            field_info += " (required)"
                        if desc:
                            field_info += f"\n    {desc}"
                        print(field_info)
            else:
                print("No schema validation defined")
            
            # Print indexes
            print("\nIndexes:")
            indexes = db[collection_name].list_indexes()
            for index in indexes:
                index_fields = []
                for field, direction in index['key'].items():
                    direction_str = ' DESC' if direction == -1 else ''
                    index_fields.append(f"{field}{direction_str}")
                
                index_info = f"  - {', '.join(index_fields)}"
                if index.get('unique'):
                    index_info += " (unique)"
                print(index_info)
            
            print("")
            
    except Exception as e:
        print(f"Error printing schema: {str(e)}")
        raise

def main():
    """Main function to initialize the database"""
    try:
        db_instances = init_mongodb()
        logger.info("Database initialized with collections:")
        for name, db in db_instances.items():
            logger.info(f"- {name}: {db.collection.name}")
        
        # Print table structure
        print_table_structure()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 