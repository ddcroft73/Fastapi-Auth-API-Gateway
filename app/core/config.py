import os
from pydantic import BaseSettings
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator

class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    API_KEY: str = os.getenv("API_KEY")

    PROJECT_NAME = 'Life Package'


    CELERY_BROKER_URL: str = os.getenv('CELERY_BROKER_URL') #"redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = os.getenv('CELERY_RESULT_BACKEND') #"redis://redis:6379/0"

    FIRST_SUPERUSER: EmailStr = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD")

    LOG_DIRECTORY: str = "./logs" # Always put the log directory in the CWD, off the main entry point.
    LOG_ARCHIVE_DIRECTORY: str = f"{LOG_DIRECTORY}/log-archives"
    DEFAULT_LOG_FILE: str = f"{LOG_DIRECTORY}/DEFAULT-app-logs.log"  # This where all log entries go If a destination is not specified.
    
    BACKEND_CORS_ORIGINS: List[str] = [
        'http://192.168.12.218:3001', # Laptop
        'http://192.168.12.189:3000', # Desktop
        'http://192.168.12.189:8015', # Desktop
        'http://localhost:3000', 
        'http://localhost:3001',
        'http://192.168.12.114',
    ] 

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

    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    VERIFYEMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1

    TWO_FACTOR_AUTH_EXPIRE_MINUTES: int = 10
    ADMIN_TOKEN_EXPIRE_MINUTES: int = 30 

    # 
    # DEVelopment IP addresses
    #  
    #    TODO:  Get rid of all this shit. Implement a virual network for the docker containers and 86 all this confusing BS. Originally
    #    I Did this so I could host either API fron my laptop or Desktop but that really makes no fucking sense because All APIs will be
    #    hosted from the same machine. Desktop, Laptop will just be Server. 
    #     Client is the Front end
    #              
    # Server
    SERVER_PORT: str = "8015"
    EMAIL_PORT: str = "8014"    
    DESKTOP_SERVER: str = f"http://192.168.12.189:{SERVER_PORT}"
    LAPTOP_SERVER: str = f"http://192.168.12.218:{SERVER_PORT}"
    # Client
    CLIENT_DESKTOP_PORT: str = "3000"
    CLIENT_LAPTOP_PORT: str = "3001"
    DESKTOP_CLIENT: str = f"http://192.168.12.189:{CLIENT_DESKTOP_PORT}"
    LAPTOP_CLIENT: str = f"http://192.168.12.218:{CLIENT_LAPTOP_PORT}"
    
    REMOTE: str = DESKTOP_SERVER  # Changes depending on the computer the server is runnnign on
    LOCAL: str = f"http://localhost:{SERVER_PORT}"    
    
    # Final access to this server
    SERVER_HOST: str = LOCAL                 
    '''
       Reconfigue this API to use a virtual network. 
    '''
    # WHen using Docker if you are running more than one service on the same computer in order for one to connect to the 
    # other you need to get the outer IP address. Only one can use localhost.  In this setup, the email service is 
    # on the same computer. and this server (AUTH) will be localhost. Or it can use it's outer IP address. 
    EMAIL_SERVICE_HOST: str = f"http://{os.getenv('HOST_IP_ADDRESS')}:{EMAIL_PORT}"  
    # 
    #  END DEV addresses
    #

    EMAILS_ENABLED: bool = True  # Off to debug
    SEND_2FA_NOTIFICATIONS: bool = True
    EMAIL_FROM: EmailStr = 'ddc.dev.python@gmail.com' # until I get a domain (decide on a name), and an email service with the same name
    USERS_OPEN_REGISTRATION: bool = True
    # This data is added to the API_KEY in order to create the Admin Token. This ensures that the Admin token is totally
    # unique from a normal "user" access token that is issued with succesful login. This effectively chnages to another API Key
    # Does it make the app more secure? IDK bt it raises the level of complexity... slightly. 
    ADMIN_API_KEY: str = 'HDG673L2MNDUI76E'    
  
settings = Settings()
