from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import UsersGroups, User
from database.users_groups import UserGroupRole


class UsersGroupsService:
    @staticmethod
    async def get_user_group(user_id: int,
                             group_id: int,
                             session: AsyncSession) -> UsersGroups:
        query = await session.execute(select(UsersGroups)
                                      .where(UsersGroups.user_id == user_id,
                                             UsersGroups.group_id == group_id))
        user_group = query.scalars().first()
        return user_group

    @staticmethod
    async def get_user_groups_teacher_or_admin(user_id: int,
                                               group_id: int,
                                               session: AsyncSession) -> UsersGroups:
        query = await session.execute(select(UsersGroups)
                                      .where(UsersGroups.user_id == user_id,
                                             UsersGroups.group_id == group_id,
                                             UsersGroups.role != UserGroupRole.STUDENT))
        user_group = query.scalars().first()
        return user_group

    @staticmethod
    async def get_group_users(group_id: int,
                              session: AsyncSession) -> List[User]:
        query = await session.execute(select(UsersGroups).join(UsersGroups.user)
                                      .where(UsersGroups.group_id == group_id,
                                             UsersGroups.role == UserGroupRole.STUDENT)
                                      .options(joinedload(UsersGroups.user))
                                      .order_by(User.last_name.asc()))
        group_users = query.scalars().all()
        return group_users
