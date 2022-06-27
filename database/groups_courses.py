from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database.base_meta import BaseSQLAlchemyModel


class GroupsCourses(BaseSQLAlchemyModel):
    __tablename__ = "dbo_groups_courses"

    group_id = Column(ForeignKey("dbo_group.id"), primary_key=True)
    course_id = Column(ForeignKey("dbo_course.id"), primary_key=True)

    group = relationship("Group", back_populates="courses")
    course = relationship("Course", back_populates="groups")
