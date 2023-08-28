from app.email_templates.verify_email import build_template_verify, build_template_reset
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from app import schemas
from jose import jwt

from app.core.config import settings

# 
# Connect with the Notifications API here
#  

def send_email(email: schemas.Email) -> None:   
   #Make this function the abstraction to the API Call
   pass

def send_test_email(email_to: str) -> None:
    pass

def verify_email(email_to: str, email_username: str, token: str) -> None:
    '''
       Send this user an email with a link to an endpoint that will:
       1. Update their is_verified field to True
       2. LOad the Login Page
    '''
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Verify Email {email_username}"
    server_host = settings.SERVER_HOST

    link = f"{server_host}/verify-email?token={token}"
    #
    # I need to send the user an email via the notif service with the abpve link
    # 
    email_outgoing: str = schemas.Email(
        email_to=email_to,
        email_from=settings.EMAIL_FROM,
        subject=subject,
        message=build_template_verify(link), # This is the HTML for the message
        user_id=email_username
    )

    # Connect to the Email API and send the email to this User.... They now have 24 hours 
    # to respond


def send_reset_password_email(email_to: str, email_username: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email_username}"
    #with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
    #    template_str = f.read()
    server_host = settings.SERVER_HOST

    link = f"{server_host}/reset-password?token={token}"
    #
    # I need to send the user an email via the notif service with the abpve link
    # 
    email_outgoing = schemas.Email(
        email_to=email_to,
        email_from=settings.EMAIL_FROM,
        subject=subject,
        message=build_template_reset(link), # This is the HTML for the message
        user_id=email_username
    )

    '''
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )'''
    


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    # I need to design an email foe verifying email account.
    # insert a link to clixk and when they ckick it, it goes to the users dashboard. 


    '''project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )
'''
    pass

def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, settings.API_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.API_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
        return None
    

def generate_verifyemail_token() -> str:
    # VERIFY_EMAIL_EXPIRE_HOURS
    pass    