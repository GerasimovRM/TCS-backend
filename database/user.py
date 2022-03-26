from enum import IntEnum

from sqlalchemy.orm import relationship

from . import Base
from sqlalchemy import Integer, String, Column, Enum


class UserStatus(IntEnum):
    ACTIVE: int = 1
    BLOCKED: int = 2
    UNDEFINED: int = -1


class User(Base):
    __tablename__ = "dbo_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(32))
    last_name = Column(String(30))
    middle_name = Column(String(30), nullable=True)
    password = Column(String(1000), nullable=True)
    vk_id = Column(String(20), nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.UNDEFINED)
    vk_access_token = Column(String(200), nullable=True)
    avatar_url = Column(String(200), nullable=True)

    groups = relationship("UsersGroups", back_populates="user")
    refresh_token = relationship("RefreshToken", back_populates="user")
    solutions = relationship("Solution", back_populates="user")
