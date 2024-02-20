
from app.email_templates.verify_email import build_template_verify 
from app.email_templates.password_reset import build_pword_reset_template

from datetime import datetime, timedelta
from typing import Optional
from app import schemas
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
import requests
from app.core.config import settings
from app.utils.api_logger import logzz
from pydantic.networks import EmailStr



"""
  I need to find a more permanent Home for this script.
"""

async def send_email(email: schemas.Email, token: str) -> None:   
    '''
    Sends a request to the Notification API, to send an Email. THis function sends requests
    to the endpoint that utilizes Celery to send the emails using a task Queue. 

    To change to the endpoint that uses asynchronous only, change send-emal to send-async.
    in the url string. 
    '''
    email_service_host = settings.EMAIL_SERVICE_HOST
    url = f'{email_service_host}/api/v1/mail/send-email/'  
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


async def send_sms(
        msg: str, 
        cell_number: str, 
        provider: str, 
        token: str
) -> None:
    '''
       
    '''

async def verify_email(email_to: str, email_username: str, token: str) -> None:
    '''
    send user an email. They need to click the embedded link to verify.
    '''
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Verify Your Email - {email_username}"
    
    # Using CLIENT_SERVER because I want to be able to test from any device on the test network.
    # if I use localhost for instance, I cant use my cellphone to verify because it cant send to localhost. needs the network IP
   # server_host: str = settings.DESKTOP_SERVER
    client_host: str = settings.DESKTOP_CLIENT
    link = f"{client_host}/routing-verify-email?token={token}"

    #link = f"{server_host}/api/v1/auth/verify-email?token={token}"   

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
    client_host = settings.DESKTOP_CLIENT

    #
    # The link should send the user to the frontend. A component that requests a password
    # and the confirmation of said pasword. and then its sent to da server to save as new.         
    #
    #link = f"{server_host}api/v1/auth/reset-password?token={token}"    # NOPE!

    link: str = f"{client_host}/password-reset?token={token}"

    reset_password = schemas.Email(
        email_to=email_to,
        email_from=settings.EMAIL_FROM,
        subject=subject,
        message=build_pword_reset_template(
            link=link, proj_name=project_name, email=email_username
        ), 
        user_id=email_username
    )     
    await send_email(reset_password, token)
    

def generate_password_reset_token(email: EmailStr) -> str:
    '''
     creates tokens used for password recovery and email verification
    '''
    delta = timedelta(hours=settings.VERIFYEMAIL_RESET_TOKEN_EXPIRE_HOURS)

    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
         "exp": exp, 
         "nbf": now, 
         "email": email 
        }, 
        settings.API_KEY, settings.ALGORITHM,
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

