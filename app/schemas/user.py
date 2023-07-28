from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    id: Optional[int]
    uuid: Optional[str]
    user_id: Optional[str]
    password: Optional[str]


class UserCreate(UserBase):
    uuid: str
    user_id: str
    password: str


class UserUpdate(UserBase):
    id: int
    pass


class UserResponse(UserBase):
    class Config:
        orm_mode = True