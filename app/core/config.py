import os
from pydantic import BaseSettings


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    API_KEY: str = os.getenv("API_KEY")
    PROJECT_NAME: str = 'dmsPlus Auth Gateway'

    CELERY_BROKER_URL: str ="redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str ="redis://redis:6379/0"

    #SQLALCHEMY_DATABASE_URI: str = "postgresql://localhost:5432/fastapi_db"

    class Config:
        env_file = "../.env"


settings = Settings()
