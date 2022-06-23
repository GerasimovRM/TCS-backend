from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Lesson


class LessonService:
    @staticmethod
    async def get_lesson(lesson_id: int,
                         session: AsyncSession) -> Lesson:
        query = await session.execute(select(Lesson)
                                      .where(Lesson.id == lesson_id))
        lesson = query.scalars().first()
        return lesson