from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.base_meta import BaseSQLAlchemyModel


class CoursesLessons(BaseSQLAlchemyModel):
    __tablename__ = "dbo_courses_lessons"

    lesson_id = Column(ForeignKey("dbo_lesson.id"), primary_key=True)
    course_id = Column(ForeignKey("dbo_course.id"), primary_key=True)
    is_hidden = Column(Boolean, default=True)
    queue_number = Column(Integer, nullable=True)

    lesson = relationship("Lesson", back_populates="courses")
    course = relationship("Course", back_populates="lessons")
