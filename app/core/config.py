import os
from pydantic import BaseSettings
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator

class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    API_KEY: str = os.getenv("API_KEY")

    PROJECT_NAME: str = 'Life\After Life Package'

    CELERY_BROKER_URL: str = os.getenv('CELERY_BROKER_URL') #"redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = os.getenv('CELERY_RESULT_BACKEND') #"redis://redis:6379/0"

    FIRST_SUPERUSER: EmailStr = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD")

    LOG_DIRECTORY: str = "./logs" # Always put the log directory in the CWD, off the main entry point.
    LOG_ARCHIVE_DIRECTORY: str = f"{LOG_DIRECTORY}/log-archives"
    DEFAULT_LOG_FILE: str = f"{LOG_DIRECTORY}/DEFAULT-app-logs.log"  # This where all log entries go If a destination is not specified.
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        'http://localhost:3001', 
        'http://localhost', 
        'http://localhost:3000'       
    ]  # development: FrontEnd

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
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    TWO_FACTOR_AUTH_EXPIRE_MINUTES: int = 10
    VERIFY_EMAIL_EXPIRE_HOURS: int= 24
    ADMIN_TOKEN_EXPIRE_TIME_MINUTES: int = 10

    #
    # FOR DEVELOPMENT ONLY:
    #   The IP Address of the machine is picked up dynamically before the stack starts. Since the services are all in docker
    #   containers, I need the actual machine IP Address to be able to send requests to the email service, or any other
    #   service on the dev machine. localhost would work fine for this service. but not for others I need to contact. 
    #   I had a couple other choice, Dedicated Docker Network, or add all services to the same docker-compose file, but 
    #   this approach seems easy enough. 
    #
    SERVER_HOST: str = f"http://localhost:8015"  
    EMAIL_API_HOST: str = f"http://{os.getenv('HOST_IP_ADDRESS')}:8014" #/192.168.12.130 This is dynamic, hence the code. 
    
    EMAILS_ENABLED: bool = True  #Off to debug
    EMAIL_FROM: EmailStr = 'ddc.dev.python@gmail.com' # until I get a domain (decide on a name), and an email service with the same name
    USERS_OPEN_REGISTRATION: bool = True
    # This data is added to the API_KEY in order to create the Admin Token. This ensures that the Admin token is totally
    # diffferent than a normal "user" token that is issued with succesful login. This effectively chnages to another API Key
    ADMIN_API_KEY: str = 'HDG673L2MNDUI76E'
    
  
settings = Settings()
