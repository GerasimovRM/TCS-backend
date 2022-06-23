from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import LessonsTasks


class LessonsTasksService:
    @staticmethod
    async def get_lesson_task(lesson_id: int,
                              task_id: int,
                              session: AsyncSession) -> LessonsTasks:
        query = await session.execute(select(LessonsTasks)
                                      .where(LessonsTasks.lesson_id == lesson_id,
                                             LessonsTasks.task_id == task_id))
        lesson_task = query.scalars().first()
        return lesson_task


