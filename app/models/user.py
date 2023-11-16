from sqlalchemy import Column, Integer, String
from app.database.base_class import Base
from sqlalchemy.dialects.postgresql import UUID  

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), unique=True, index=True, nullable=False)  
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    phone_number = Column(String, unique=False, index=True, nullable=True) 
    cell_provider = Column(String, unique=False, index=False, nullable=True) 
    is_verified = Column(Boolean(), default=False)
    is_loggedin = Column(Boolean(), default=False)
    
    account = relationship("Account", uselist=False, back_populates="user")
