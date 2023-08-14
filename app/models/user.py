from sqlalchemy import Column, Integer, String
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, Integer, String
#from sqlalchemy.orm import relationship
from app.database.base_class import Base

# phone_number
# is_verified: 
# failed_attempts
# account_locked

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    #New fields
    phone_number = Column(String, unique=False, index=True, nullable=True) 
    is_verified = Column(Boolean(), default=False)
    failed_attempts = Column(Integer, default=0)
    account_locked = Column(Boolean(), default=False)
