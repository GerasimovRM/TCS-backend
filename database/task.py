from enum import IntEnum

from sqlalchemy import Column, Integer, String, Float, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from database import Base
from database.solution import SolutionStatus


class Task(Base):
    __tablename__ = "dbo_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))
    description = Column(String(4000), nullable=True)
    max_score = Column(Float)
    attachments = Column(JSON)

    lessons = relationship("LessonsTasks", back_populates="task")
    solutions = relationship("Solution", back_populates="task")
    chat_messages = relationship("ChatMessage", back_populates="task")
