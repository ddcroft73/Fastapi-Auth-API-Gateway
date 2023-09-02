from pydantic import BaseModel
from pydantic.networks import EmailStr
from typing import Optional
   
class Email(BaseModel):
    email_to: EmailStr
    email_from: EmailStr
    subject: str
    message: str     
    user_id: Optional[str] = None


class MailResponse(BaseModel):
    result: str

class BasicResponse(BaseModel):
    result: str    

class ResendVerification(BaseModel):
    email: EmailStr    