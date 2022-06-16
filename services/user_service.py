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

