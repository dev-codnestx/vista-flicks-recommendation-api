from fastapi import APIRouter
from app.routes.api.v1.reels import router as reels_router

api_v1_router = APIRouter()
api_v1_router.include_router(reels_router, prefix="/v1", tags=["Reels"])
