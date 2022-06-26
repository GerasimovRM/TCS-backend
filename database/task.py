from enum import IntEnum

from sqlalchemy import Column, Integer, String, Float, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from database import Base
from database.base_meta import SQLAlchemyBase
from database.solution import SolutionStatus


class TaskType(IntEnum):
    CLASS_WORK = 1
    HOME_WORK = 2
    ADDITIONAL_WORK = 3


class Task(SQLAlchemyBase):
    __tablename__ = "dbo_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))
    description = Column(String(4000), nullable=True)
    max_score = Column(Float)
    attachments = Column(JSON)
    task_type = Column(Enum(TaskType))


    lessons = relationship("LessonsTasks", back_populates="task")
    solutions = relationship("Solution", back_populates="task")
    chat_messages = relationship("ChatMessage", back_populates="task")
