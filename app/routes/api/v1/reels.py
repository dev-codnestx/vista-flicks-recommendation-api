from fastapi import APIRouter, Query
from app.database import reels_collection, feed_collection
from app.schemas.reels import ReelSchema
from pymongo import ASCENDING

router = APIRouter(prefix="/reels", tags=["Reels"])

# Global cache for feed data (Replace with Redis for scaling)
cached_feed_data = []

async def get_feed_data():
    global cached_feed_data
    if not cached_feed_data:
        cached_feed_data = [
            {**feed, "_id": str(feed["_id"])}
            async for feed in feed_collection.find().sort("position", ASCENDING)
        ]
    return cached_feed_data

@router.get("/feed")
async def get_reels_feed(page: int = Query(1, ge=1), limit: int = Query(10, le=50)):

    # ✅ Fetch feed data from cache or DB
    feed_data = cached_feed_data or await get_feed_data()
    
    # ✅ Create position map
    position_map = {"adscampaign": [], "reviewvideos": [], "reel": []}
    for item in feed_data:
        position_map[item["type"].lower()].append(item["position"])

    # 🟢 Step 1: Get total count of valid "live" reels
    total_count = await reels_collection.count_documents({
        "videoUrl": {"$ne": None},
        "status": "live"
    })

    # Calculate total pages
    total_pages = (total_count // limit) + (1 if total_count % limit else 0)

    # If page is out of range, return empty response
    if page > total_pages:
        return {
            "result": {
                "data": [],
                "pagination": {
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "limit": limit
                }
            }
        }

    # 🟣 Step 2: Fetch "live" reels based on feed mapping
    response_array = []
    for feed_type, positions in position_map.items():
        count = len(positions)

        if count > 0:
            fetched_reels = []
            async for reel in reels_collection.aggregate([
                {"$match": {"type": feed_type, "videoUrl": {"$ne": None}, "status": "live"}},
                {"$sample": {"size": count}}
            ]):
                reel_data = ReelSchema.from_mongo(reel).dict()  # Convert to dictionary
                reel_data["_id"] = str(reel["_id"])  # Add _id to response
                fetched_reels.append(reel_data)

            # ✅ Assign positions correctly
            for index, reel in enumerate(fetched_reels):
                if index < len(positions):
                    response_array.append({
                        "position": positions[index],
                        "type": feed_type,
                        "data": reel
                    })

    # 🟠 Step 3: Apply Pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    # ✅ Ensure we fetch additional reels if `response_array` is too small
    if len(response_array) < end_idx:
        remaining_needed = end_idx - len(response_array)

        async for reel in reels_collection.find(
            {"videoUrl": {"$ne": None}, "status": "live"}
        ).skip(start_idx + len(response_array)).limit(remaining_needed):
            reel_data = ReelSchema.from_mongo(reel).dict()  # Convert to dictionary
            reel_data["_id"] = str(reel["_id"])  # Add _id to response

            # ✅ Assign missing type and position
            response_array.append({
                "position": start_idx + len(response_array) + 1,
                "type": reel["type"],
                "data": reel_data
            })

    # ✅ Apply final pagination
    paginated_data = response_array[start_idx:end_idx]

    return {
        "result": {
            "data": paginated_data,
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit
            }
        }
    }



@router.get("/feeds")
async def get_reels(limit: int = Query(10, le=50)):
    # Fetch "live" reels of type "reel"
    response_array = []
    async for reel in reels_collection.aggregate([
    {"$match": {"videoUrl": {"$ne": None}, "status": "live", "type": "reel"}},
    {"$sample": {"size": limit}}]):
        response_array.append(str(reel["_id"]))  # Provide only ObjectIds

    return {"reels": response_array}