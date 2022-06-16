from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import User


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
