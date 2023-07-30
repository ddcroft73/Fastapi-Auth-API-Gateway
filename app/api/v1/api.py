

from fastapi import APIRouter 
from .routers.users import router as users_router
from .routers.login import router as auth_router
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(
    users_router, 
    prefix='/users', 
    tags=["users"]
)

api_router.include_router(
    auth_router, 
    prefix='/auth', 
    tags=["login"]
)