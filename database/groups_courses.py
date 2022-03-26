from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class GroupsCourses(Base):
    __tablename__ = "dbo_groups_courses"

    group_id = Column(ForeignKey("dbo_group.id"), primary_key=True)
    course_id = Column(ForeignKey("dbo_course.id"), primary_key=True)

    group = relationship("Group", back_populates="courses")
    course = relationship("Course", back_populates="groups")
