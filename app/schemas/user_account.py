from .user import UserBase
from .account import AccountBase
from datetime import datetime

class AccountResp(AccountBase):
    pass

class UserResp(UserBase):
    account: AccountResp
    