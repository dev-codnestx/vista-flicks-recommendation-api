from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["vistaFlicks_dev"]  # Replace with your actual DB name
reels_collection = db["reels"]
feed_collection = db["feeds"]
