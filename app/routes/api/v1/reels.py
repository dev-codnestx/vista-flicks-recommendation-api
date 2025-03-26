from fastapi import APIRouter, Query, HTTPException
from app.database import reels_collection, feed_collection
from app.schemas.reels import ReelSchema
from pymongo import ASCENDING

router = APIRouter(prefix="/reels", tags=["Reels"])

@router.get("/feed")
async def get_reels_feed(page: int = Query(1, ge=1), limit: int = Query(10, le=50)):
    # 🟢 Step 1: Get total count of valid "live" reels
    total_count = await reels_collection.count_documents({
        "videoUrl": {"$ne": None},  # ✅ Only count reels with videoUrl
        "status": "live"  # ✅ Only count reels with status "live"
    })
    # print(f"🟢 Total count of valid live reels: {total_count}")

    # Calculate total pages
    total_pages = (total_count // limit) + (1 if total_count % limit else 0)
    # print(f"🟢 Total pages: {total_pages}")

    # If page is out of range, return empty response
    if page > total_pages:
        # print(f"⚠️ Requested page {page} is out of range (Total pages: {total_pages})")
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

    # 🟡 Step 2: Fetch all feed data (sorted by position)
    feed_data = []
    async for feed in feed_collection.find().sort("position", ASCENDING):
        feed["_id"] = str(feed["_id"])  # Convert ObjectId to string
        feed_data.append(feed)

    # print(f"🟡 Total feed items fetched: {len(feed_data)}")

    # 🔵 Step 3: Organize positions
    position_map = {"adsCampaign": [], "reviewVideos": [], "reel": []}
    for item in feed_data:
        feed_type = item["type"]
        position = item["position"]
        if feed_type in position_map:
            position_map[feed_type].append(position)

    # print("🔵 Position Map:", position_map)

    # 🟣 Step 4: Fetch only "live" reels from DB
    response_array = []
    for feed_type, positions in position_map.items():
        count = len(positions)
        # print(f"🟠 Fetching {count} reels for type: {feed_type}")

        if count > 0:
            fetched_reels = []
            async for reel in reels_collection.aggregate([
                {"$match": {"type": feed_type, "videoUrl": {"$ne": None}, "status": "live"}},  # ✅ Only fetch "live" reels
                {"$sample": {"size": count}}
            ]):
                reel_data = ReelSchema.from_mongo(reel)
                fetched_reels.append(reel_data)

            # print(f"🟡 Fetched {len(fetched_reels)} valid live reels for {feed_type}")

            # Assign positions correctly
            for index, reel in enumerate(fetched_reels):
                if index < len(positions):
                    response_array.append({
                        "position": positions[index],
                        "type": feed_type,
                        "data": reel
                    })

    # print(f"🔴 Final response array length before pagination: {len(response_array)}")

    # 🟠 Step 5: Apply Pagination (Fixed ✅)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    # print(f"🔵 Pagination indices: start={start_idx}, end={end_idx}")

    # ✅ Ensure we fetch additional reels if `response_array` is too small
    if len(response_array) < end_idx:
        remaining_needed = end_idx - len(response_array)
        # print(f"⚠️ Not enough reels in response_array, fetching {remaining_needed} more from DB...")

        async for reel in reels_collection.find(
            {"videoUrl": {"$ne": None}, "status": "live"},  # ✅ Fetch only "live" reels
        ).skip(start_idx).limit(remaining_needed):
            reel_data = ReelSchema.from_mongo(reel)
            response_array.append(reel_data)

    # ✅ Apply pagination correctly
    paginated_data = response_array[start_idx:end_idx]
    # print(f"🟢 Paginated data length: {len(paginated_data)}")

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
