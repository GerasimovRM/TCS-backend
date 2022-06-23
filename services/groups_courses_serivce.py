from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import GroupsCourses


class GroupsCoursesService:
    @staticmethod
    async def get_group_course(group_id: int,
                               course_id: int,
                               session: AsyncSession) -> GroupsCourses:
        query = await session.execute(select(GroupsCourses)
                                      .where(GroupsCourses.group_id == group_id)
                                      .where(GroupsCourses.course_id == course_id))
        group_course = query.scalars().first()
        return group_course

    @staticmethod
    async def get_group_course_with_courses(group_id: int,
                                            course_id: int,
                                            session: AsyncSession) -> GroupsCourses:
        query = await session.execute(select(GroupsCourses)
                                      .where(GroupsCourses.group_id == group_id)
                                      .where(GroupsCourses.course_id == course_id)
                                      .options(joinedload(GroupsCourses.course)))
        group_course = query.scalars().first()
        return group_course
