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
    current_date: str = datetime.now().strftime('%m/%d/%Y')
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "user_role": user_role, 
        "creation_date": current_date
    }
    encoded_jwt = jwt.encode(to_encode, settings.API_KEY, algorithm=settings.ALGORITHM)    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Still working on this
def verify_admin_token( token: str) -> bool:
    '''
    payload = jwt.decode(
            token, settings.API_KEY, algorithms=[settings.ALGORITHM]
        )
    token_data = schemas.TokenPayload(**payload)
    

    user = crud.user.get(db, model_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")'''
    
    return True


def generate_singleuse_token(user_id: int, expire_minutes: int = 2) -> str:
    '''
    I need tokens all over that are simple and meant for verification and login
    purposes, or just to connect to another API. 
    '''
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {
        "exp": expire, 
        "sub": user_id
    }
    encoded_jwt = jwt.encode(to_encode, settings.API_KEY, algorithm=settings.ALGORITHM)    
    return encoded_jwt


def verify_2FA():
    return


def verify_token(token: str) -> bool:
    '''
      Verifies a token in the most basic way. Is it from this system, and has it expired.
    '''
    try:
        payload = jwt.decode(
                token, settings.API_KEY, algorithms=[settings.ALGORITHM]
            )
        
    except (JWTError, ValidationError):
        return False    
    return True


def send_2FA_code(
    user_id: int ,        
    user_email: str,           
    user_phone_number: str,  
    contact_method_2FA: str            
) -> schemas.TwoFactorAuth:
    
    '''
      Generates and sends a 2FA code to the user via sms or email.
    '''      
    def generate_2FA_code() -> str:
        '''
        Generates a 2FA code.
        Code should be 6 Characters letters and numbers
        ex. B5R-922 or XXR-XNR, etc.
        '''  
        characters = string.ascii_uppercase + "0123456789"
        code_2FA = "".join(choice(characters) if pos != 3 else "-"  for pos in range(7)) 
        return code_2FA
    

    code_2FA: str = generate_2FA_code()
    token_2FA: str = generate_singleuse_token(
        user_id, 
        settings.TWO_FACTOR_AUTH_EXPIRE_MINUTES
    )
    
    
    if contact_method_2FA == "sms":
        message: str = (f"Your {settings.PROJECT_NAME} verification code is: {code_2FA} "
                        f"\nThis code will expire in {settings.TWO_FACTOR_AUTH_EXPIRE_MINUTES} minutes. "
                        "Do not share this code with anyone.")
        send_sms(message, user_phone_number, token_2FA)

    elif contact_method_2FA == "email":
        email_obj = schemas.Email(
            email_to="life.package.web@gmail.com", # email_for_2FA
            email_from=settings.EMAIL_FROM,
            subject="Two Factor Authentication Code from Life Package",
            message=build_template_2FA_code(code_2FA=code_2FA, email=user_email),
            user_id=user_email
        )
        send_email(email_obj, token_2FA)       
    
    return schemas.TwoFactorAuth(code=code_2FA, token=token_2FA) 
