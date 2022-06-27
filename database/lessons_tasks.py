from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from database.base_meta import Base, SQLAlchemyAdditional


class LessonsTasks(Base, SQLAlchemyAdditional):
    __tablename__ = "dbo_lessons_tasks"

    lesson_id = Column(ForeignKey("dbo_lesson.id"), primary_key=True)
    task_id = Column(ForeignKey("dbo_task.id"), primary_key=True)
    queue_number = Column(Integer)

    lesson = relationship("Lesson", back_populates="tasks")
    task = relationship("Task", back_populates="lessons")
