
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_verified: Optional[bool] = False
    failed_login_attempts: Optional[int] = 0


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    user_uuid: uuid.UUID = Field(default_factory=uuid.uuid4)

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None
    user_uuid: uuid.UUID  # All users have a uuid, but its unchangeable.

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
