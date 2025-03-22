from fastapi import FastAPI
from app.routes.api import api_router

app = FastAPI(title="Vista ML API", version="0.0.1")

app.include_router(api_router)

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}
