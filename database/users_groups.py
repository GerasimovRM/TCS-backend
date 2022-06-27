from enum import IntEnum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database.base_meta import BaseSQLAlchemyModel


class UserGroupRole(IntEnum):
    STUDENT: int = 0
    TEACHER: int = 1
    OWNER: int = 2


class UsersGroups(BaseSQLAlchemyModel):
    __tablename__ = "dbo_users_groups"

    user_id = Column(ForeignKey("dbo_user.id"), primary_key=True)
    group_id = Column(ForeignKey("dbo_group.id"), primary_key=True)
    role = Column(Enum(UserGroupRole))

    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="users")


