#New schema for the accunt table.

# When I make this I need to think about how i will recieve this data from an api. 
#etc.. etc. Basicallyuse user as a road map, and feel around till its right.
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

# Shared properties
class AccountBase(BaseModel):
    account_creation_date: Optional[datetime]      #
    subscription_type: str = 'free'    #
    last_login_date: Optional[datetime]
    bill_renew_date: Optional[datetime]    #
    auto_renewal: bool = False        #
    account_status_reason: Optional[str] = None
    cancellation_date: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    last_account_changes_date: Optional[datetime]
    account_last_update_date: Optional[datetime]
    preferred_contact_method: Optional[str] = 'email'  #
    timezone: Optional[str] = ' '   #

    #  mm/dd/yyyy Howwe do it my part of the world.
    # THe Database isexpecting datetime objects for all dates... I prefer to work with strings in my code and I can stick to a format
    # easy enough, so I will parse the strings to objects to be used in the DB
    @validator('cancellation_date', pre=True, always=True)
    def parse_cancellation_date(cls, date: str) -> datetime:
        if date:
            return datetime.strptime(date, '%m/%d/%Y')
        return None    

    @validator('account_creation_date', pre=True, always=True)
    def parse_account_creation_date(cls, date: str) -> Optional[datetime]:
        if date:
            return datetime.strptime(date, '%m/%d/%Y')
        return None

    @validator('account_last_update_date', pre=True, always=True)
    def parse_account_last_update_date(cls, date: str) -> Optional[datetime]:
        if date:
            return datetime.strptime(date, '%m/%d/%Y')
        return None

    @validator('last_account_changes_date', pre=True, always=True)
    def parse_account_changes_date(cls, date: str) -> Optional[datetime]:
        if date:
            return datetime.strptime(date, '%m/%d/%Y')
        return None
    
    @validator('last_login_date', pre=True, always=True)
    def parse_last_login_date(cls, date: str) -> Optional[datetime]:
        if date:
            return datetime.strptime(date, '%m/%d/%Y')
        return None
    
    @validator('bill_renew_date', pre=True, always=True)
    def parse_bill_renew_date(cls, date: str) -> Optional[datetime]:
        if date:
            return datetime.strptime(date, '%m/%d/%Y')
        return None


class AccountCreate(AccountBase):
    admin_PIN: Optional[str]  # should be optional because will only be used by the admins

# Properties to receive via API on update
class AccountUpdate(AccountBase):
    subscription_type: Optional[str]
    auto_renewal: Optional[bool]    
    preferred_contact_method: Optional[str]
    

class AccountInDBBase(AccountBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class Account(AccountInDBBase):
    pass

# Additional properties stored in DB
class AccountInDB(AccountInDBBase):
    hashed_admin_PIN: str
