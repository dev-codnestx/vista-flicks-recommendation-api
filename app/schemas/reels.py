from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

class ReelSchema(BaseModel):
    reelId: str
    uploadedBy: str  # Convert ObjectId to string
    views: int
    tags: list
    isDeleted: bool
    videoName: str
    videoContentType: str
    company: str
    isApproved: bool
    status: str
    comments: list
    createdAt: str  # Convert datetime to string
    updatedAt: str  # Convert datetime to string

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to Pydantic model."""
        if "_id" in data:
            data["_id"] = str(data["_id"])  # Convert ObjectId to string
        if "uploadedBy" in data:
            data["uploadedBy"] = str(data["uploadedBy"])  # Convert uploadedBy to string
        if "company" in data:
            data["company"] = str(data["company"])  # Convert company to string
        if "createdAt" in data and isinstance(data["createdAt"], datetime):
            data["createdAt"] = data["createdAt"].isoformat()  # Convert datetime to ISO format
        if "updatedAt" in data and isinstance(data["updatedAt"], datetime):
            data["updatedAt"] = data["updatedAt"].isoformat()  # Convert datetime to ISO format
        return cls(**data)
