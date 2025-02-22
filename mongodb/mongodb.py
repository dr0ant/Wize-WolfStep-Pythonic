import os
import yaml
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Dict, Any
from datetime import datetime, timezone

class MongoDBConnector:
    def __init__(self, config_path: str = ".config/mongodb_connection_string.yaml", env: str = "dev"):
        """
        Initialize the MongoDB connector with a YAML config file.

        Args:
            config_path (str): Path to the YAML configuration file.
            env (str): Environment to use (dev, uat, prod). Defaults to 'dev'.
        """
        self.config_path = config_path
        self.env = os.getenv("MONGO_ENV", env)  # Override with env var if set
        self.config = self._load_config()
        self.client = None
        self.db = None
        self._connect()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load the MongoDB configuration from the YAML file.

        Returns:
            Dict[str, Any]: Configuration dictionary for the specified environment.

        Raises:
            FileNotFoundError: If the config file doesn't exist.
            KeyError: If the environment is not found in the config.
        """
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                if "mongodb" not in config or self.env not in config["mongodb"]:
                    raise KeyError(f"Environment '{self.env}' not found in {self.config_path}")
                return config["mongodb"][self.env]
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

    def _connect(self) -> None:
        """
        Establish a connection to MongoDB using the loaded configuration.

        Raises:
            ConnectionFailure: If the connection to MongoDB fails.
        """
        try:
            self.client = MongoClient(self.config["uri"])
            # Test the connection
            self.client.admin.command("ping")
            self.db = self.client[self.config["database"]]
            print(f"Connected to MongoDB: {self.config['database']} (env: {self.env})")
        except ConnectionFailure as e:
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")

    def get_database(self):
        """
        Get the MongoDB database object.

        Returns:
            pymongo.database.Database: The connected database.
        """
        if self.db is None:
            raise RuntimeError("Not connected to MongoDB")
        return self.db

    def get_collection(self, collection_name: str):
        """
        Get a specific MongoDB collection.

        Args:
            collection_name (str): Name of the collection.

        Returns:
            pymongo.collection.Collection: The requested collection.
        """
        return self.get_database()[collection_name]

    def close(self) -> None:
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
            self.client = None
            self.db = None

    def __enter__(self):
        """
        Enable use with context manager (with statement).
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensure connection is closed when exiting context.
        """
        self.close()


# Example usage
"""

if __name__ == "__main__":
    # Optionally set environment variable in shell: export MONGO_ENV=dev
    connector = MongoDBConnector()

    # Access the 'posts' collection and insert a sample document
    posts_collection = connector.get_collection("posts")
    sample_post = {
        "_id": "test-post-001",
        "geolocation": {"type": "Point", "coordinates": [-73.935242, 40.730610]},
        "created_at": datetime.now(timezone.utc),
        "title": "Test Post",
        "text": "This is a test post for WolfStep!",
        "medias": [],
        "views_count": 0,
        "like_count": 0,
        "reply_count": 0
    }
    posts_collection.insert_one(sample_post)

    # Query a document
    retrieved = posts_collection.find_one({"_id": "test-post-001"})
    print("Retrieved post:", retrieved)

    # Close connection
    connector.close()

"""