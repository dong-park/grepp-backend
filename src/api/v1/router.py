from fastapi import APIRouter
from src.api.v1.endpoints import users
from src.api.v1.endpoints import reservations

router = APIRouter()

router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
router.include_router(users.router, prefix="/users", tags=["users"])
