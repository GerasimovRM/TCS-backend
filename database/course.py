from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base
from database.base_meta import SQLAlchemyBase


class Course(SQLAlchemyBase):
    __tablename__ = "dbo_course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))
    description = Column(String(2000), nullable=True)

    groups = relationship("GroupsCourses", back_populates="course")
    lessons = relationship("CoursesLessons", back_populates="course")
    solutions = relationship("Solution", back_populates="course")
    chat_messages = relationship("ChatMessage", back_populates="course")
