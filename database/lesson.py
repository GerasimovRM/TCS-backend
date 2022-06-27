from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base_meta import BaseSQLAlchemyModel


class Lesson(BaseSQLAlchemyModel):
    __tablename__ = "dbo_lesson"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))
    description = Column(String(2000), nullable=True)

    courses = relationship("CoursesLessons", back_populates="lesson")
    tasks = relationship("LessonsTasks", back_populates="lesson")