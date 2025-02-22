from typing import List, Dict, Optional, Union
from datetime import datetime
import uuid
from pymongo import GEOSPHERE

# Assuming MongoDB connection is set up elsewhere
# Example: client = MongoClient("mongodb://localhost:27017/"); db = client["wolfstep"]

class Post:
    def __init__(
        self,
        uid: str = None,
        parent_uid: Optional[str] = None,
        longitude: float = 0.0,
        latitude: float = 0.0,
        created_at: Optional[datetime] = None,
        title: str = "",
        text: str = "",
        medias: List[Dict[str, Union[str, None]]] = None,
        views_count: int = 0,
        like_count: int = 0,
        reply_count: int = 0
    ):
        """
        Initialize a WolfStep Post object.

        Args:
            uid (str): Unique identifier for the post (auto-generated if None).
            parent_uid (Optional[str]): UID of the parent post if a reply, None otherwise.
            longitude (float): Longitude coordinate in decimal degrees.
            latitude (float): Latitude coordinate in decimal degrees.
            created_at (Optional[datetime]): Timestamp of creation (defaults to now if None).
            title (str): Short title of the post (max 100 chars).
            text (str): Main content of the post (max 280 chars).
            medias (List[Dict]): List of media objects with type, url, and optional description.
            views_count (int): Number of views.
            like_count (int): Number of likes.
            reply_count (int): Number of replies.
        """
        self.uid = uid if uid else str(uuid.uuid4())  # Generate UUID if not provided
        self.parent_uid = parent_uid
        self.geolocation = {
            "type": "Point",
            "coordinates": [longitude, latitude]  # [lon, lat] per GeoJSON
        }
        self.created_at = created_at if created_at else datetime.utcnow()
        self.title = title[:100]  # Enforce max length
        self.text = text[:280]   # Enforce max length
        self.medias = medias if medias is not None else []
        self.views_count = max(0, views_count)  # Ensure non-negative
        self.like_count = max(0, like_count)
        self.reply_count = max(0, reply_count)

    def to_mongo_dict(self) -> Dict:
        """
        Convert the Post object to a MongoDB-compatible dictionary.
        """
        return {
            "_id": self.uid,  # Use uid as MongoDB's primary key
            "parent_uid": self.parent_uid,
            "geolocation": self.geolocation,
            "created_at": self.created_at.isoformat(),  # Store as ISO string
            "title": self.title,
            "text": self.text,
            "medias": self.medias,
            "views_count": self.views_count,
            "like_count": self.like_count,
            "reply_count": self.reply_count
        }

    @classmethod
    def from_mongo_dict(cls, mongo_data: Dict) -> 'Post':
        """
        Create a Post object from a MongoDB document.

        Args:
            mongo_data (Dict): MongoDB document data.
        """
        return cls(
            uid=mongo_data["_id"],
            parent_uid=mongo_data.get("parent_uid"),
            longitude=mongo_data["geolocation"]["coordinates"][0],
            latitude=mongo_data["geolocation"]["coordinates"][1],
            created_at=datetime.fromisoformat(mongo_data["created_at"]),
            title=mongo_data["title"],
            text=mongo_data["text"],
            medias=mongo_data["medias"],
            views_count=mongo_data["views_count"],
            like_count=mongo_data["like_count"],
            reply_count=mongo_data["reply_count"]
        )

    def validate(self) -> bool:
        """
        Basic validation to ensure data integrity.
        """
        if not isinstance(self.uid, str) or not self.uid:
            return False
        if len(self.title) > 100 or len(self.text) > 280:
            return False
        if not isinstance(self.geolocation["coordinates"], list) or len(self.geolocation["coordinates"]) != 2:
            return False
        for media in self.medias:
            if "type" not in media or "url" not in media:
                return False
            if media["type"] not in ["image", "audio", "video", "file"]:
                return False
        return True

# Example usage with MongoDB integration
if __name__ == "__main__":
    from pymongo import MongoClient

    # Sample post
    post = Post(
        longitude=-73.935242,
        latitude=40.730610,
        title="Morning Walk",
        text="Exploring the park with my wolf pack! #WolfStep",
        medias=[
            {
                "type": "image",
                "url": "https://example.com/wolfstep/post123/image1.jpg",
                "description": "A pixel wolf in the wild"
            }
        ]
    )

    # Validate
    print("Is valid?", post.validate())  # True

    # Convert to MongoDB format
    mongo_data = post.to_mongo_dict()
    print("MongoDB data:", mongo_data)

    # Simulate MongoDB interaction
    client = MongoClient("mongodb://localhost:27017/")
    db = client["wolfstep"]
    
    # Create a 2dsphere index for geospatial queries
    db.posts.create_index([("geolocation", GEOSPHERE)])

    # Insert post
    db.posts.insert_one(mongo_data)

    # Retrieve and recreate Post object
    retrieved = db.posts.find_one({"_id": post.uid})
    recreated_post = Post.from_mongo_dict(retrieved)
    print("Recreated post text:", recreated_post.text)