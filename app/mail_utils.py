
from app.email_templates.verify_email import build_template_verify 
from app.email_templates.password_reset import build_pword_reset_template

from datetime import datetime, timedelta, timezone
from typing import Optional
from app import schemas
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
#import requests  # pretty sure I 86'd this for httpx async
from app.core.config import settings
from app.utils.api_logger import logzz
from pydantic.networks import EmailStr
import httpx



"""
  I need to find a more permanent Home for this script.
"""

async def send_email(email: schemas.Email, token: str) -> None:   
    '''
        Sends a request to the Notification API, to send an Email. This function sends requests
        to the endpoint that utilizes Celery to send the emails using a task Queue. 

        To change to the endpoint that uses asynchronous only, change send-emal to send-async.
        in the url string. 

        Parameters:
        - email: An instance of the Email schema, containing the email details such as sender, recipient, subject, and body.
        - token: A string representing the JWT token for authorization.

        Returns:
        - None

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
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=email.dict())
        return response.json()

async def send_sms(
        user_id: int,
        username: str,
        msg: str, 
        cell_number: str, 
        provider: str, 
        token: str
) -> None:
    '''
    Sends an SMS message using an external API. 
    (The notifications API that is apart of this backend)
    
    Args:
        user_id (int): THe Id of the user as it is in the database.
        username (str): The username or usr email of the account holder.
        msg (str): The message to be sent in the SMS.
        cell_number (str): The cell number to which the SMS should be sent.
        provider (str): The SMS service provider to be used.
        token (str): The authentication token required for accessing the SMS service API.
        
    Returns:
        None
    '''
    email_service_host = settings.EMAIL_SERVICE_HOST
    url = f'{email_service_host}/api/v1/sms/send-email-sms/'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'message': msg,
        'phone_number': cell_number,
        'provider': provider,
        'user_id': user_id,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            # Log the user ID,  and the number the message was sent to:
            logzz.info(f"SMS sent to: Username\email: {username}, User Number: {cell_number}", timestamp=True)
        else:    
            logzz.error(f"Failed to send SMS: {response.text}", timestamp=True)


async def verify_email(
        email_to: str, email_username: str, token: str
) -> None:
    '''
    Asynchronously verifies the user's email address by sending an email and awaits the response.

    Parameters:
    - email_to (str): The email address of the recipient.
    - email_username (str): The username associated with the email address.
    - token (str): The JWT token for authorization.

    Returns:
    - None

    Raises:
    - None

    '''
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Verify Your Email - {email_username}"
        
    client_host: str = settings.DESKTOP_CLIENT
    link = f"{client_host}/routing-verify-email?token={token}"


    verify_Email = schemas.Email(
        email_to=email_to,
        email_from=settings.EMAIL_FROM,
        subject=subject,
        message=build_template_verify(link, project_name), # This is the HTML for the message
        user_id=email_username
    )
    await send_email(verify_Email, token)


async def send_reset_password_email(email_to: str, email_username: str, token: str) -> None:
    '''
    Sends a reset password email to the specified email address.

    Parameters:
    - email_to: A string representing the email address of the recipient.
    - email_username: A string representing the username associated with the email address.
    - token: A string representing the JWT token for authorization.

    Returns:
    - None
    '''    
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

    now = datetime.now(timezone.utc)
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

