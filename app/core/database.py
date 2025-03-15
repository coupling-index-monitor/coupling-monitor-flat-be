import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid
from neo4j import GraphDatabase
from app.core.config import settings


class DatabaseManager:
    def __init__(self):
        # MongoDB variables
        self.mongo_client = None
        self.trace_collection = None
        self.trace_updates = None
        self.trace_collection_updates = None

        # Neo4j driver
        self.neo4j_driver = None

    async def initialize_mongo(self):
        """
        Initialize MongoDB connection and collections.
        """
        try:
            # Connect to MongoDB
            self.mongo_client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
            self.mongo_client.admin.command("ping")
            db = self.mongo_client[settings.MONGO_DB]

            # Explicitly check or create collections
            if "traces" not in db.list_collection_names():
                db.create_collection("traces")
            if "trace_updates" not in db.list_collection_names():
                db.create_collection("trace_updates")
            if "trace_collection_updates" not in db.list_collection_names():
                db.create_collection("trace_collection_updates")

            # Assign collections
            self.trace_collection = db["traces"]
            self.trace_updates = db["trace_updates"]
            self.trace_collection_updates = db["trace_collection_updates"]

            print(f"MongoDB connected successfully. Collections initialized: ")
                #   f"trace_collection={self.trace_collection}, trace_updates={self.trace_updates}")
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            raise e

    async def close_mongo(self):
        """
        Close MongoDB connection.
        """
        if self.mongo_client is not None:
            self.mongo_client.close()
            print("MongoDB connection closed.")
        else:
            print("MongoDB client was not initialized.")

    def initialize_neo4j(self):
        """
        Initialize Neo4j connection.
        """
        try:
            # Connect to Neo4j
            self.neo4j_driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            self.neo4j_driver.verify_connectivity()
            print("Neo4j connected successfully.")
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            raise e

    def close_neo4j(self):
        """
        Close Neo4j connection.
        """
        if self.neo4j_driver is not None:
            self.neo4j_driver.close()
            print("Neo4j connection closed.")
        else:
            print("Neo4j driver was not initialized.")

    def get_trace_collection(self):
        """
        Get MongoDB 'traces' collection.
        """
        if self.trace_collection is None:
            raise RuntimeError("MongoDB 'traces' collection is not initialized.")
        return self.trace_collection

    def get_trace_updates_collection(self):
        """
        Get MongoDB 'trace_updates' collection.
        """
        if self.trace_updates is None:
            raise RuntimeError("MongoDB 'trace_updates' collection is not initialized.")
        return self.trace_updates

    def get_trace_collection_updates_collection(self):
        """"
        Get MongoDB 'trace_collection_updates' collection
        """
        if self.trace_collection_updates is None:
            raise RuntimeError("MongoDB 'trace_collection_updates' collection is not initialized.")
        return self.trace_collection_updates


# Instantiate a global DatabaseManager
db_manager = DatabaseManager()
