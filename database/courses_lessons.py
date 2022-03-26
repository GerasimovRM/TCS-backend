from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class CoursesLessons(Base):
    __tablename__ = "dbo_courses_lessons"

    lesson_id = Column(ForeignKey("dbo_lesson.id"), primary_key=True)
    course_id = Column(ForeignKey("dbo_course.id"), primary_key=True)

    lesson = relationship("Lesson", back_populates="courses")
    course = relationship("Course", back_populates="lessons")
