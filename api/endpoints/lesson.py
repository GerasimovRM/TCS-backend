from typing import Optional, List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import LessonDto
from models.site.lesson import LessonsResponse, LessonResponse
from services.auth_service import get_current_active_user
from database import User, Group, get_session, GroupsCourses, Course, CoursesLessons

router = APIRouter(
    prefix="/lesson",
    tags=["lesson"]
)


@router.get("/get_all", response_model=LessonsResponse)
async def get_lessons(group_id: int,
                      course_id: int,
                      current_user: User = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)) -> LessonsResponse:
    # check group access
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id))

    user_group = query.scalars().first()
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    query = await session.execute(select(GroupsCourses)
                                  .where(GroupsCourses.group_id == group_id,
                                         GroupsCourses.course_id == course_id))
    # check group access
    group_course = query.scalars().first()
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    query = await session.execute(select(Course)
        .where(Course.id == group_course.course_id)
        .options(
        joinedload(Course.lessons).joinedload(CoursesLessons.lesson)))
    course = query.scalars().first()
    lessons_dto = list(map(lambda t: LessonDto.from_orm(t.lesson), course.lessons))
    return LessonsResponse(lessons=lessons_dto,
                           course_name=course.name,
                           course_description=course.description)


@router.get("/get_one", response_model=LessonResponse)
async def get_lesson(group_id: int,
                     course_id: int,
                     lesson_id: int,
                     current_user: User = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)) -> LessonResponse:
    # check group access
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id))

    user_group = query.scalars().first()
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    query = await session.execute(select(GroupsCourses)
                                  .where(GroupsCourses.group_id == group_id,
                                         GroupsCourses.course_id == course_id))
    # check group access
    group_course = query.scalars().first()
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    query = await session.execute(select(CoursesLessons)
                                  .where(CoursesLessons.course_id == course_id,
                                         CoursesLessons.lesson_id == lesson_id)
                                  .options(joinedload(CoursesLessons.lesson)))
    course_lesson = query.scalars().first()
    return LessonResponse.from_orm(course_lesson.lesson)
