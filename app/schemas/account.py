from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from app.utils.api_logger import logzz
import re

# Shared properties
class AccountBase(BaseModel):
    user_id: int   # Add this line
    creation_date:  Union[datetime, str, None] = Field(..., example="01/23/2022")
    subscription_type: str = 'free' # free, basic, premium, maybe one other. Need to figure this out
    last_login_date:  Union[datetime, str, None] = Field(..., example="01/23/2022")   # Has not logged in yet, None is valid at creation
    bill_renew_date:  Union[datetime, str, None] = Field(None, example="01/23/2022")  # Dont know, free account None should be fine.
    auto_bill_renewal: bool = False

    cancellation_date:  Union[datetime, str, None] = Field(None, example="01/23/2022")
    cancellation_reason: Optional[str] = None

    last_update_date:   Union[datetime, str, None] = Field(None, example="01/23/2022")
    preferred_contact_method: Optional[str] = 'email' # email, sms
    account_locked: Optional[bool] = False
    account_locked_reason: Optional[str] = None  # Account can be locked if any weird shit ensues, and fot faile login attempts.
    timezone: Optional[str] = None

class AccountCreate(AccountBase):
    user_id: Optional[int]
    admin_PIN: Optional[str]   

# Properties to receive via API on update
class AccountUpdate(AccountBase):
    pass
    '''
    subscription_type: Optional[str]
    auto_bill_renewal: Optional[bool]
    preferred_contact_method: Optional[str]
    cancellation_date: Union[datetime, str, None]
    cancellation_reason: Optional[str] = None'''
   
class AccountInDBBase(AccountBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class Account(AccountInDBBase):
    pass

# Additional properties stored in DB
class AccountInDB(AccountInDBBase):
    hashed_admin_PIN: Optional[str] = None # This only comes into play if the account is an admin account
