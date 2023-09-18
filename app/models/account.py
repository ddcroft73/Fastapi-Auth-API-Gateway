# Add code for account table

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id')) 
    hashed_admin_PIN = Column(String, nullable=True)  # This unlike the pasword can be empty.
    creation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_update_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    subscription_type = Column(String, default='free')  # Defaulted to 'free'
    last_login_date = Column(DateTime(timezone=True), nullable=True)
    bill_renew_date = Column(DateTime(timezone=True), nullable=True)
    auto_bill_renewal = Column(Boolean, default=False)
    account_locked = Column(Boolean(), default=False)
    account_locked_reason = Column(String, nullable=True)
    cancellation_date = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String, nullable=True)
    preferred_contact_method = Column(String, default='email')
    timezone = Column(String, nullable=True)  

    user = relationship("User", back_populates="account")


# Do I need to add the times here if Im already in the DB?