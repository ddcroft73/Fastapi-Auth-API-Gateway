from fastapi import FastAPI
from app.api.v1.api import api_router
from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_V1_STR)