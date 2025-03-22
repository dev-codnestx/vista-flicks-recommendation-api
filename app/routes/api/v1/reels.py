from fastapi import APIRouter, Depends
from app.database import reels_collection
from app.schemas.reels import ReelSchema
from typing import List

router = APIRouter(prefix="/reels", tags=["Reels"])

@router.get("/", response_model=List[ReelSchema])
async def get_reels():
    reels = []
    async for reel in reels_collection.aggregate([{"$sample": {"size": 5}}]):  # Random 5 reels
        reels.append(ReelSchema.from_mongo(reel))

    # print("Length of reels:", len(reels))
    return reels
