from pymongo import MongoClient
import json
from bson import json_util
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def print_table_structure():
    """Print MongoDB collections structure based on actual data"""
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017')
    db = client['yt_digest']
    
    # Get all collections
    collections = db.list_collection_names()
    
    print("\nDatabase Structure:")
    print("===================")
    
    for collection_name in collections:
        print(f"\nCollection: {collection_name}")
        print("-" * (len(collection_name) + 11))
        
        # Get collection
        collection = db[collection_name]
        
        # Get one document to analyze structure
        sample_doc = collection.find_one()
        if not sample_doc:
            print("(Empty collection)")
            continue
            
        # Get validation rules if they exist
        validation_rules = db.command("listCollections", 
                                    filter={"name": collection_name})
        validator = None
        for doc in validation_rules['cursor']['firstBatch']:
            if 'options' in doc and 'validator' in doc['options']:
                validator = doc['options']['validator']
                
        # Print document structure
        def print_structure(doc, indent=2):
            for key, value in doc.items():
                if key == '_id':
                    continue
                    
                # Get field type
                field_type = type(value).__name__
                
                # Check if field is required from validator
                required = False
                if validator and '$jsonSchema' in validator:
                    schema = validator['$jsonSchema']
                    if 'required' in schema and key in schema['required']:
                        required = True
                
                # Print field info
                print(" " * indent + f"{key}: {field_type}")
                if required:
                    print(" " * (indent + 2) + "(Required)")
                
                # Recursively print nested documents
                if isinstance(value, dict):
                    print_structure(value, indent + 2)
        
        print_structure(sample_doc)
        
        # Print total documents
        doc_count = collection.count_documents({})
        print(f"\nTotal documents: {doc_count}")

if __name__ == "__main__":
    print_table_structure() 