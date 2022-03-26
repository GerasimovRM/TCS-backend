from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Group(Base):
    __tablename__ = "dbo_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))

    users = relationship("UsersGroups", back_populates="group")
    courses = relationship("GroupsCourses", back_populates="group")
    solutions = relationship("Solution", back_populates="group")
    chat_messages = relationship("ChatMessage", back_populates="group")
