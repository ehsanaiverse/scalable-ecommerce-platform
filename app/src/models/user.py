from sqlalchemy import Column, String, Integer

from app.src.db.database import Base

class User(Base):
    __tablename__ = "usertable"
    
    id=Column(Integer, primary_key=True, index=True)
    fullname=Column(String, nullable=False)
    email=Column(String, unique=True, nullable=False)
    password=Column(String, nullable=False, index=True)
    role=Column(String, default='User')
    otp=Column(Integer, index=True)