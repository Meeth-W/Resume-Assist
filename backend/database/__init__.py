from pymongo import MongoClient
from bson import ObjectId
import os
from typing import Any, Dict, List, Optional, Union

# Unused so far, but will be useful later for the AI based features
class Database:
    def __init__(self, collection_name: str):
        """
        Initialize Database class for a specific collection.

        Args:
            collection_name (str): The name of the MongoDB collection to operate on.
        """
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "resume_assist")
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    # ------------------- Insert Operations -------------------

    def insert(self, document: Dict[str, Any]) -> str:
        """Insert a single document and return its ID."""
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents and return their IDs."""
        result = self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    # ------------------- Find Operations -------------------

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the query."""
        return self.collection.find_one(query)

    def find_by_id(self, doc_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Find a document by its ObjectId."""
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        return self.collection.find_one({"_id": doc_id})

    def find_all(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find all documents matching the query."""
        return list(self.collection.find(query or {}))

    # ------------------- Update Operations -------------------

    def update_one(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update a single document and return modified count."""
        result = self.collection.update_one(query, {"$set": update_data})
        return result.modified_count

    def update_by_id(self, doc_id: Union[str, ObjectId], update_data: Dict[str, Any]) -> int:
        """Update a document by its ID."""
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        result = self.collection.update_one({"_id": doc_id}, {"$set": update_data})
        return result.modified_count

    # ------------------- Delete Operations -------------------

    def delete_one(self, query: Dict[str, Any]) -> int:
        """Delete a single document matching the query."""
        result = self.collection.delete_one(query)
        return result.deleted_count

    def delete_by_id(self, doc_id: Union[str, ObjectId]) -> int:
        """Delete a document by its ObjectId."""
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        result = self.collection.delete_one({"_id": doc_id})
        return result.deleted_count

    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents matching the query."""
        result = self.collection.delete_many(query)
        return result.deleted_count

    # ------------------- Utility Methods -------------------

    def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching the query."""
        return self.collection.count_documents(query or {})

    def drop_collection(self):
        """Drop the entire collection."""
        self.collection.drop()

    def list_collections(self) -> List[str]:
        """List all collections in the database."""
        return self.db.list_collection_names()

    def exists(self, query: Dict[str, Any]) -> bool:
        """Check if a document exists for the given query."""
        return self.collection.find_one(query) is not None
