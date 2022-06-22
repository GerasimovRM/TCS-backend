from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import CoursesLessons


class CoursesLessonsService:
    @staticmethod
    async def get_course_lesson(course_id: int,
                                lesson_id: int,
                                session: AsyncSession) -> CoursesLessons:
        query = await session.execute(select(CoursesLessons)
                                      .where(CoursesLessons.course_id == course_id,
                                             CoursesLessons.lesson_id == lesson_id))
        course_lesson = query.scalars().all()
        return course_lesson

    @staticmethod
    async def get_course_lessons(course_id: int,
                                 session: AsyncSession) -> List[CoursesLessons]:
        query = await session.execute(select(CoursesLessons)
                                      .where(CoursesLessons.course_id == course_id)
                                      .options(joinedload(CoursesLessons.lesson)))
        course_lessons = query.scalars().all()
        return course_lessons

    @staticmethod
    async def get_course_lesson_with_lesson(course_id: int,
                                            lesson_id: int,
                                            session: AsyncSession) -> CoursesLessons:
        query = await session.execute(select(CoursesLessons)
                                      .where(CoursesLessons.course_id == course_id,
                                             CoursesLessons.lesson_id == lesson_id)
                                      .options(
            joinedload(CoursesLessons.lesson)
        ))
        course_lesson = query.scalars().all()
        return course_lesson
