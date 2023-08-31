import os
from pydantic import BaseSettings
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
from app.utils.utils import get_host_ip
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    API_KEY: str = os.getenv("API_KEY")

    PROJECT_NAME: str = 'Dead Mans Switch... PLUS!'

    CELERY_BROKER_URL: str ="redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str ="redis://redis:6379/0"

    FIRST_SUPERUSER: EmailStr = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD")

    LOG_DIRECTORY: str = "./logs" # Always put the log directory in the CWD, off the main entry point.
    LOG_ARCHIVE_DIRECTORY: str = f"{LOG_DIRECTORY}/log-archives"
    DEFAULT_LOG_FILE: str = f"{LOG_DIRECTORY}/DEFAULT-app-logs.log"  # This where all log entries go If a destination is not specified.
    
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost:3001', 'http://localhost'] # development: FrontEnd

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    VERIFY_EMAIL_EXPIRE_HOURS: int= 24
    SERVER_HOST: str = 'http://192.168.12.218:8015' #'http://localhost:8015'
    EMAIL_API_SERVER: str = 'http://192.168.12.218:8014'#f'http://{get_host_ip()}:8000' #'http://192.168.12.218:8014'   # Write a function to return this address
    EMAILS_ENABLED: bool = True
    EMAIL_FROM: EmailStr = 'ddc.dev.python@gmail.com'
    # This will be the link to get to the users DashBoard, or homepage
    VERIFY_EMAIL_LINK: AnyHttpUrl = None
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        env_file = "../.env"


settings = Settings()
