from fastapi import FastAPI, HTTPException

from src.api.error_handler import exception_handler
from src.api.v1.router import router as api_router

app = FastAPI()
app.add_exception_handler(HTTPException, exception_handler)
app.include_router(api_router, prefix="/v1")
