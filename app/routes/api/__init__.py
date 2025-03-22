from fastapi import APIRouter
from app.routes.api.v1 import api_v1_router

api_router = APIRouter()
api_router.include_router(api_v1_router, prefix="/api")
