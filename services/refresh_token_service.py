from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import RefreshToken


class RefreshTokenService:
    @staticmethod
    async def get_refresh_token(refresh_token: str,
                                session: AsyncSession) -> RefreshToken:
        query = await session.execute(select(RefreshToken)
                                      .where(RefreshToken.token == refresh_token)
                                      .options(joinedload(RefreshToken.user)))
        db_refresh_token = query.scalars().first()
        return db_refresh_token
