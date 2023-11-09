from typing import Optional, Union
from pydantic import BaseModel

class TwoFactorAuth(BaseModel):
    code: str
    token: str