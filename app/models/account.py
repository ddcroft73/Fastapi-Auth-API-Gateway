# Add code for account table

from sqlalchemy import Column, Integer, String
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, Integer, String
#from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    # ...