from pymongo import MongoClient
import logging
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def empty_mongodb():
    """Empty all collections in the database"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['yt_digest']
        logger.info("Connected to MongoDB")

        # Get all collections
        collections = db.list_collection_names()
        
        # Empty each collection
        for collection_name in collections:
            collection = db[collection_name]
            result = collection.delete_many({})
            logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")

        logger.info("Database emptied successfully")
        return True

    except Exception as e:
        logger.error(f"Error emptying database: {str(e)}")
        raise

def confirm_empty():
    """Ask for user confirmation before emptying database"""
    response = input("Are you sure you want to empty all collections? This cannot be undone! (yes/no): ")
    return response.lower() == 'yes'

def main():
    """Main function to empty the database"""
    try:
        if confirm_empty():
            empty_mongodb()
            logger.info("Database emptying completed")
        else:
            logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Failed to empty database: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 