from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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

    @staticmethod
    async def get_lesson_tasks(lesson_id: int,
                               session: AsyncSession) -> List[LessonsTasks]:
        query = await session.execute(select(LessonsTasks)
                                      .where(LessonsTasks.lesson_id == lesson_id)
                                      .options(joinedload(LessonsTasks.task)))
        lesson_tasks = query.scalars().all()
        return lesson_tasks


