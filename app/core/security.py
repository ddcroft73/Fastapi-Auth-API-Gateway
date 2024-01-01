from datetime import datetime, timedelta
from typing import Any, Union, Optional

from fastapi import HTTPException, status

from jose import jwt
from passlib.context import CryptContext
from pydantic.networks import EmailStr
from .config import settings
import string

from jose.exceptions import ExpiredSignatureError, JWTError
from pydantic import ValidationError

from app.database.session import SessionLocal

from app.utils.api_logger import logzz

from app import schemas
from app.email_templates.email_2FA_code import build_template_2FA_code
from app.mail_utils import send_email, send_sms
from random import choice
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def create_access_token(
    subject: Union[str, Any], user_role: str, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    current_date: str = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "user_role": user_role, 
        "creation_date": current_date
    }
    encoded_jwt = jwt.encode(to_encode, settings.API_KEY, algorithm=settings.ALGORITHM)    
    return encoded_jwt


def create_admin_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    '''
        The token an admin must use to perform any actions on other users, or on the 
        system in general. This token will be good for no more than 1/2 hour. 
        This token uses a variation of the Applications API key.
    '''
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ADMIN_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire, 
        "sub": str(subject) # The users ID
    }

    API_KEY: str = settings.API_KEY + settings.ADMIN_API_KEY
    encoded_jwt = jwt.encode(to_encode, API_KEY, algorithm=settings.ALGORITHM)   

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Still working on this
def verify_admin_token(token: str) -> bool:
    '''
        delete all this and just use verify_token?
        Right now Im just sending them through for debugging
    '''

    API_KEY: str = settings.API_KEY + settings.ADMIN_API_KEY
    try:
        jwt.decode(
            token, API_KEY, algorithms=[settings.ALGORITHM]
        )  
        
    except (JWTError, ValidationError):
        return False      
    
    return True



def generate_singleuse_token(user_id: int, email: str, expire_minutes: int = 5) -> str:
    '''
        I need tokens all over that are simple and meant for verification and 
        to connect to another API.  It will always be tied to the user and have
        an expiration date.
    '''
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {
        "exp": expire, 
        "sub": str(user_id),
        "email": email
    }
    encoded_jwt = jwt.encode(to_encode, settings.API_KEY, algorithm=settings.ALGORITHM)    
    return encoded_jwt


def verify_2FA(users_code: str, real_code: str):
    '''
      Compares the token from the User and the token that was created to see if match
    '''    
    if users_code != real_code:
        return False
    return True


def verify_token(token: str) -> bool:
    '''
       Used tokens dealing with 2fa. and single tokens used to send requests to 
       other APIS.
    '''
    try:
        jwt.decode(
            token, settings.API_KEY, algorithms=[settings.ALGORITHM]
        )  
        
    except (JWTError, ValidationError):
        return False           
    return True


def email_from_token(token: str) -> str:
    '''
    Extracts the email address from a token. This is sused to compare the email in a token
    to an email of a user when verifying 2fa, etc.
    '''
    _token = jwt.decode(
        token, settings.API_KEY, algorithms=[settings.ALGORITHM]
    )
    return _token["email"]



async def send_2FA_code(
    user_id: int ,        
    contact_method_2FA: str,        
    user_email: str,           
    user_phone_number: str=None,      
    user_role: str=None
) -> schemas.TwoFactorAuth:    
    '''
      Generates and sends a 2FA code to the user via sms or email.
    '''      
    def generate_2FA_code() -> str:
        '''
        Generates a 2FA code.
        Code should be 6 Characters letters and numbers
        ex. B5R922 or XXRXNR, etc.
        '''  
        characters = string.ascii_uppercase + "0123456789"
        code_2FA = "".join(choice(characters) for _ in range(6)) 
        return code_2FA
    

    code_2FA: str = generate_2FA_code()
    token_2FA: str = generate_singleuse_token(
        user_id=user_id, email=user_email, expire_minutes=settings.TWO_FACTOR_AUTH_EXPIRE_MINUTES
    )    
    

    if contact_method_2FA in ["sms", "cell", "text"]:
        message: str = (f"Your {settings.PROJECT_NAME} verification code is: {code_2FA} "
                        f"\n\nThis code will expire in {settings.TWO_FACTOR_AUTH_EXPIRE_MINUTES} minutes. "
                        "Do not share this code with anyone.")
        
        if settings.SEND_2FA_NOTIFICATIONS:
            await send_sms(
                msg=message, cell_number=user_phone_number, token=token_2FA
            )
     
    elif contact_method_2FA == "email":
        email_obj = schemas.Email(
            email_to=user_email, 
            email_from=settings.EMAIL_FROM,
            subject="Two Factor Authentication Code from Life Package",
            message=build_template_2FA_code(code_2FA=code_2FA, email=user_email),
            user_id=user_email
        )
        if settings.SEND_2FA_NOTIFICATIONS:
           await send_email(email=email_obj, token=token_2FA)      
    
    return schemas.TwoFactorAuth(
        code=code_2FA, token=token_2FA, user_role=user_role
    ) 
