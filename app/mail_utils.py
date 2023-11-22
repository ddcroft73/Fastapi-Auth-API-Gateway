from app.email_templates.verify_email import build_template_verify, build_template_reset
from datetime import datetime, timedelta
from typing import Optional
from app import schemas
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
import requests
from app.core.config import settings
from app.utils.api_logger import logzz
from pydantic.networks import EmailStr

# I need to come up with a more secure way to communicate with the email service. Just a token
# is not good enough

async def send_email(email: schemas.Email, token: str) -> None:   
    '''
    Sends a request to the Notification API, to send an Email
    '''
    email_api_host = settings.EMAIL_API_HOST
    url = f'{email_api_host}/api/v1/mail/send-email/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    logzz.info(
        f'Sending Request to Notification service. Email Sent to: {email.email_to}', 
        timestamp=True
    )
    
    response = requests.request(
            "POST", 
            url, 
            headers=headers, 
            json=email.dict()
        )
    return response.json()

async def send_sms(msg: str, cell_number: str, token: str) -> None:
    ''''''

async def verify_email(email_to: str, email_username: str, token: str) -> None:
    '''
    send user an email. They need to click the embedded link to verify
    '''
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Verify Your Email - {email_username}"
    server_host = settings.SERVER_HOST
    #
    # Still deciding if I want this link to point to the FE, and then back to BE, or leave it
    # and send the user from the BE then to the FE.
    #
    link = f"{server_host}/api/v1/auth/verify-email?token={token}"
    # resend_link = f'{server_host}/api/v1/auth/resend-verification?email={email_username}'
    
    verify_Email = schemas.Email(
        email_to=email_to,
        email_from=settings.EMAIL_FROM,
        subject=subject,
        message=build_template_verify(link, project_name), # This is the HTML for the message
        user_id=email_username
    )
    await send_email(verify_Email, token)

async def send_reset_password_email(email_to: str, email_username: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email_username}"
    server_host = settings.SERVER_HOST    
    #
    # As with email Verify, Link HEre, Or FE???
    #
    link = f"{server_host}/api/v1/auth/reset-password?token={token}"    
    reset_password = schemas.Email(
        email_to=email_to,
        email_from=settings.EMAIL_FROM,
        subject=subject,
        message=build_template_reset(link, project_name), # This is the HTML for the message
        user_id=email_username
    )     
    await send_email(reset_password, token)
    

def generate_password_reset_token(email: EmailStr) -> str:
    '''
     creates tokens used for password recovery and email verification
    '''
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
         "exp": exp, 
         "nbf": now, 
         "email": email 
        }, 
        settings.API_KEY, 
        settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.API_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    
    except jwt.JWTError:
        return None
    
    
def generate_verifyemail_token(email: EmailStr) -> str:
   return generate_password_reset_token(email)

def verify_emailVerify_token(token: str) ->  Optional[str]:
    return verify_password_reset_token(token)

