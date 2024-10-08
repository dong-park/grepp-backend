from fastapi import FastAPI

from src.api.v1.router import router as api_router

app = FastAPI()
app.include_router(api_router, prefix="/v1")
