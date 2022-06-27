from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import User, Admin, Teacher


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: int,
                             session: AsyncSession) -> User:
        query = await session.execute(select(User)
                                      .where(User.id == user_id))
        user = query.scalars().first()
        return user

    @staticmethod
    async def get_user_by_vk_id(vk_id: str,
                                session: AsyncSession) -> User:
        t = select(User).where(User.vk_id == vk_id)
        query = await session.execute(t)
        db_user = query.scalars().first()
        return db_user

    @staticmethod
    async def is_admin(user_id: int,
                       session: AsyncSession) -> bool:
        admin_query = await session.execute(select(Admin)
                                            .where(Admin.user_id == user_id))
        admin = admin_query.scalars().first()
        if admin:
            return True
        else:
            return False

    @staticmethod
    async def is_teacher(user_id: int,
                         session: AsyncSession) -> bool:
        teacher_query = await session.execute(select(Teacher)
                                              .where(Teacher.user_id == user_id))
        teacher = teacher_query.scalars().first()
        if teacher:
            return True
        else:
            return False

    @staticmethod
    async def is_admin_or_teacher(user_id: int,
                                  session: AsyncSession) -> bool:
        is_admin = await UserService.is_admin(user_id, session)
        if is_admin:
            return True
        is_teacher = await UserService.is_teacher(user_id, session)
        if is_teacher:
            return True
        return False
