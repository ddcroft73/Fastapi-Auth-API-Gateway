from fastapi import APIRouter 
from .routes.users import router as users_router
from .routes.login import router as auth_router
from .routes.utillity import router as utility_router
from .routes.logman import router as log_router
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

api_router.include_router(
    utility_router, 
    prefix='/util', 
    tags=["utillity"]
)

api_router.include_router(
    log_router, 
    prefix='/logs', 
    tags=["logs"]
)