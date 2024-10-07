from sqlalchemy import Column, Integer, String, Enum, func, Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True, unique=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    role = Column(Enum('user', 'moderator', 'admin', name='user_roles'), nullable=False, default="user")
    refresh_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
