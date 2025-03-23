from fastapi import APIRouter, Depends
from app.database import reels_collection, feed_collection
from app.schemas.reels import ReelSchema

router = APIRouter(prefix="/reels", tags=["Reels"])

@router.get("/reels-feed")
async def get_reels_feed():
    # Fetch all feed data
    feed_data = []
    async for feed in feed_collection.find():
        feed["_id"] = str(feed["_id"])  # Convert ObjectId to string
        feed_data.append(feed)

    # Count occurrences of each type in feed
    position_map = {"adsCampaign": [], "reviewVideos": [], "reel": []}

    for item in feed_data:
        feed_type = item["type"]
        position = item["position"]
        if feed_type in position_map:
            position_map[feed_type].append(position)  # ✅ Store all positions

    # Fetch reels based on type counts
    response_array = []

    for feed_type, positions in position_map.items():
        count = len(positions)
        if count > 0:
            fetched_reels = []
            async for reel in reels_collection.aggregate([
                {"$match": {"type": feed_type}},
                {"$sample": {"size": count}}  # Fetch exactly the number of positions
            ]):
                fetched_reels.append(ReelSchema.from_mongo(reel))  # Convert to Pydantic model

            # Assign correct positions
            for index, reel in enumerate(fetched_reels):
                response_array.append({
                    "position": positions[index],  # Ensuring correct position assignment
                    "type": feed_type,
                    "data": reel
                })

    return {"result": {"data": response_array}}
