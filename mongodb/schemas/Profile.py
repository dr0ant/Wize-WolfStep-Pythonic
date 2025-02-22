from typing import Dict, Optional
from datetime import datetime, timezone
import uuid
from pymongo import MongoClient  # For example usage only

class Profile:
    def __init__(
        self,
        uid: str = None,
        profile_creation_date: Optional[datetime] = None,
        profiles_updated_date: Optional[datetime] = None,
        user_name: str = "",
        gender: Optional[str] = None,
        birth_date: Optional[datetime] = None,
        total_post_created: int = 0,
        total_post_visited: int = 0,
        wolf_id: str = "",
        bio: str = "",
        profile_tag: str = "",
        profile_level: int = 1,
        profile_exp: int = 0
    ):
        """
        Initialize a WolfStep UserProfile object.

        Args:
            uid (str): Unique identifier for the profile (auto-generated if None).
            profile_creation_date (Optional[datetime]): Date the profile was created (defaults to now).
            profiles_updated_date (Optional[datetime]): Date the profile was last updated (defaults to now).
            user_name (str): User's display name (max 50 chars).
            gender (Optional[str]): User's gender (e.g., 'M', 'F', 'Other', None).
            birth_date (Optional[datetime]): User's birth date.
            total_post_created (int): Total number of posts created by the user.
            total_post_visited (int): Total number of posts visited by the user.
            wolf_id (str): Unique identifier for the user's wolf (e.g., pixel art reference).
            bio (str): User's bio/description (max 200 chars).
            profile_tag (str): Short tag or handle (max 20 chars, e.g., '@username').
            profile_level (int): User's level (defaults to 1).
            profile_exp (int): Experience points accumulated.
        """
        self.uid = uid if uid else str(uuid.uuid4())  # Generate UUID if not provided
        self.profile_creation_date = profile_creation_date if profile_creation_date else datetime.now(timezone.utc)
        self.profiles_updated_date = profiles_updated_date if profiles_updated_date else datetime.now(timezone.utc)
        self.user_name = user_name[:50]  # Enforce max length
        self.gender = gender
        self.birth_date = birth_date
        self.total_post_created = max(0, total_post_created)  # Ensure non-negative
        self.total_post_visited = max(0, total_post_visited)  # Ensure non-negative
        self.wolf_id = wolf_id
        self.bio = bio[:200]  # Enforce max length
        self.profile_tag = profile_tag[:20]  # Enforce max length
        self.profile_level = max(1, profile_level)  # Ensure at least level 1
        self.profile_exp = max(0, profile_exp)  # Ensure non-negative

    def to_mongo_dict(self) -> Dict:
        """
        Convert the UserProfile object to a MongoDB-compatible dictionary.
        """
        return {
            "_id": self.uid,  # Use uid as MongoDB's primary key
            "profile_creation_date": self.profile_creation_date.isoformat(),
            "profiles_updated_date": self.profiles_updated_date.isoformat(),
            "user_name": self.user_name,
            "gender": self.gender,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "total_post_created": self.total_post_created,
            "total_post_visited": self.total_post_visited,
            "wolf_id": self.wolf_id,
            "bio": self.bio,
            "profile_tag": self.profile_tag,
            "profile_level": self.profile_level,
            "profile_exp": self.profile_exp
        }

    @classmethod
    def from_mongo_dict(cls, mongo_data: Dict) -> 'Profile':
        """
        Create a UserProfile object from a MongoDB document.

        Args:
            mongo_data (Dict): MongoDB document data.
        """
        return cls(
            uid=mongo_data["_id"],
            profile_creation_date=datetime.fromisoformat(mongo_data["profile_creation_date"]),
            profiles_updated_date=datetime.fromisoformat(mongo_data["profiles_updated_date"]),
            user_name=mongo_data["user_name"],
            gender=mongo_data.get("gender"),
            birth_date=datetime.fromisoformat(mongo_data["birth_date"]) if mongo_data.get("birth_date") else None,
            total_post_created=mongo_data["total_post_created"],
            total_post_visited=mongo_data["total_post_visited"],
            wolf_id=mongo_data["wolf_id"],
            bio=mongo_data["bio"],
            profile_tag=mongo_data["profile_tag"],
            profile_level=mongo_data["profile_level"],
            profile_exp=mongo_data["profile_exp"]
        )

    def validate(self) -> bool:
        """
        Basic validation to ensure data integrity.
        """
        if not isinstance(self.uid, str) or not self.uid:
            return False
        if not isinstance(self.user_name, str) or len(self.user_name) > 50:
            return False
        if self.gender and self.gender not in ['M', 'F', 'Other', None]:
            return False
        if len(self.bio) > 200 or len(self.profile_tag) > 20:
            return False
        if not isinstance(self.wolf_id, str) or not self.wolf_id:
            return False
        if not isinstance(self.profile_level, int) or self.profile_level < 1:
            return False
        if not isinstance(self.profile_exp, int) or self.profile_exp < 0:
            return False
        return True

# Example usage with MongoDB integration
if __name__ == "__main__":
    from pymongo import MongoClient

    # Sample user profile
    profile = Profile(
        user_name="WolfLover123",
        gender="M",
        birth_date=datetime(1995, 5, 15),
        wolf_id="wolf-001",
        bio="Lover of wolves and nature.",
        profile_tag="@WolfLover"
    )

    # Validate
    print("Is valid?", profile.validate())  # True

    # Convert to MongoDB format
    mongo_data = profile.to_mongo_dict()
    print("MongoDB data:", mongo_data)

    # Simulate MongoDB interaction
    client = MongoClient("mongodb://localhost:27017/")
    db = client["wolfstep"]

    # Insert profile into 'profiles' collection
    db.profiles.insert_one(mongo_data)

    # Retrieve and recreate UserProfile object
    retrieved = db.profiles.find_one({"_id": profile.uid})
    recreated_profile = Profile.from_mongo_dict(retrieved)
    print("Recreated profile user_name:", recreated_profile.user_name)