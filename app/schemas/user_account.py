from .user import UserBase
from .account import AccountBase
from pydantic import BaseModel


class UserAccount(BaseModel):
    user: UserBase
    account: AccountBase

    class Config:
        orm_mode = True
        


