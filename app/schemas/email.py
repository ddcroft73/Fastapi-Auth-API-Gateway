# THe pydantic models that represent any emails I may need to send to the Notif API. 
# THese will most likely be Emails to verify email, recover reset password. And anything else
# I may realize I'd need to send to users. 

from pydantic import BaseModel
from typing import Optional
   
class Email(BaseModel):
    email_to: str
    email_from: str
    subject: str
    message: str     
    user_id: Optional[str] = None


class MailResponse(BaseModel):
    result: str

class BasicResponse(BaseModel):
    result: str    