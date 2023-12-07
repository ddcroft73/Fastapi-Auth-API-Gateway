from typing import Optional, Union
from pydantic import BaseModel

class AdminToken(BaseModel):
    token: str
