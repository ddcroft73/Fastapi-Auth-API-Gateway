from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import re

# Shared properties
class AccountBase(BaseModel):
    user_id: int   # This is set automatically. when the user is created, the user.id is user here to tie the account to the user.
    creation_date:  Union[datetime, str, None] = Field(None, example="01/23/2022")
    subscription_type: str = 'free' # free, basic, premium, maybe one other. Need to figure this out
    last_login_date:  Union[datetime, str, None] = Field(None, example="01/23/2022")   # Has not logged in yet, None is valid at creation
    last_logout_date: Union[datetime, str, None] = Field(None, example="01/23/2022")
    
    bill_renew_date:  Union[datetime, str, None] = Field(None, example="01/23/2022")  # Dont know, free account None should be fine.
    auto_bill_renewal: bool = False

    cancellation_date:  Union[datetime, str, None] = Field(None, example="01/23/2022")
    cancellation_reason: Optional[str] = None

    last_update_date:   Union[datetime, str, None] = Field(None, example="01/23/2022")
    preferred_contact_method: Optional[str] = 'email' # email, sms
    account_locked: Optional[bool] = False
    account_locked_reason: Optional[str] = None  # Account can be locked if any weird shit ensues, and fot faile login attempts.
    timezone: Optional[str] = None
    
    use_2FA: bool = False
    contact_method_2FA: Optional[str] = None
    cell_provider_2FA: Optional[str] = None
    

class AccountCreate(AccountBase):
    user_id: Optional[int]
    admin_PIN: Optional[str]   

# Properties to receive via API on update
class AccountUpdate(AccountBase):
    admin_PIN: Optional[str]
    
   
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
