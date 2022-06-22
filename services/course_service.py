from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Course


class CourseService:
    @staticmethod
    async def get_course(course_id: int,
                         session: AsyncSession) -> Course:
        query = await session.execute(select(Course)
                                      .where(Course.id == course_id))
        course = query.scalars().first()
        return course
