from sqlalchemy import Column, Integer, String, Float

from app.database.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    password = Column(Float, nullable=False)