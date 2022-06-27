from datetime import datetime
from enum import IntEnum

from sqlalchemy import Column, Integer, String, Float, ForeignKeyConstraint, Boolean, Enum, \
    DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.base_meta import BaseSQLAlchemyModel


class SolutionStatus(IntEnum):
    ERROR: int = -1
    ON_REVIEW: int = 0
    COMPLETE_NOT_MAX: int = 1
    COMPLETE: int = 2


class Solution(BaseSQLAlchemyModel):
    __tablename__ = "dbo_solution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(ForeignKey("dbo_task.id"))
    user_id = Column(ForeignKey("dbo_user.id"))
    course_id = Column(ForeignKey("dbo_course.id"))
    group_id = Column(ForeignKey("dbo_group.id"))

    score = Column(Integer, default=0, nullable=False)
    code = Column(String, nullable=False)
    status = Column(Enum(SolutionStatus), nullable=False, default=SolutionStatus.ON_REVIEW)
    time_start = Column(DateTime, nullable=False, default=datetime.now)
    time_finish = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="solutions")
    task = relationship("Task", back_populates="solutions")
    course = relationship("Course", back_populates="solutions")
    group = relationship("Group", back_populates="solutions")
