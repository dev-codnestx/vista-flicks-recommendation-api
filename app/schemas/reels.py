from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from typing import Optional

class ReelSchema(BaseModel):
    reelId: str
    uploadedBy: str  
    views: int
    type: str
    tags: list
    isDeleted: bool
    videoName: str
    videoContentType: str
    company: str
    isApproved: bool
    status: str
    comments: list
    createdAt: str  
    updatedAt: str  
    videoUrl: Optional[str] = None  
    description: Optional[str] = None  
    title: Optional[str] = None  

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to Pydantic model."""
        def convert_objectid(value):
            return str(value) if isinstance(value, ObjectId) else value

        data = {key: convert_objectid(value) for key, value in data.items()}  # Convert all ObjectId fields

        if "createdAt" in data and isinstance(data["createdAt"], datetime):
            data["createdAt"] = data["createdAt"].isoformat()  
        if "updatedAt" in data and isinstance(data["updatedAt"], datetime):
            data["updatedAt"] = data["updatedAt"].isoformat()  

        # ✅ Ensure missing fields are set to None instead of failing validation
        data["videoUrl"] = data.get("videoUrl", None)
        data["description"] = data.get("description", None)
        data["title"] = data.get("title", None)

        return cls(**data)
