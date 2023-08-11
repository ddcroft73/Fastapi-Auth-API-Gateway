from sqlalchemy import Column, Integer, String
from app.database.base_class import Base

from sqlalchemy import Boolean, Column, Integer, String
#from sqlalchemy.orm import relationship

from app.database.base_class import Base

# phone_number
# pin_number IDK about this....
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
    
