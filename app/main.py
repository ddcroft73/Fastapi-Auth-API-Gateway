from fastapi import FastAPI
from core import settings
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.auth import router as auth_router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(users_router, prefix=settings.API_V1_STR, tags=["Users"])
app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["Auth"])
