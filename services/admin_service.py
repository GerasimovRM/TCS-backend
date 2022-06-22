from sqlalchemy.ext.asyncio import AsyncSession

from database import Admin


class AdminService:
    @staticmethod
    async def get_admin(user_id: int,
                        session: AsyncSession) -> Admin:
        return await session.get(Admin, user_id)

