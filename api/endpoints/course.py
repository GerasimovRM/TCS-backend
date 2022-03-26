from typing import Optional, List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import CourseDto
from models.site.course import CoursesResponse, CourseResponse
from services.auth_service import get_current_active_user
from services.group_service import get_group_by_id
from database import User, Course, Group, get_session, GroupsCourses

router = APIRouter(
    prefix="/course",
    tags=["course"]
)


@router.get("/get_all", response_model=CoursesResponse)
async def get_courses(group_id: int,
                      current_user: User = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)) -> CoursesResponse:
    # check group access
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id))

    user_group = query.scalars().first()
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    query = await session.execute(select(Group)
        .where(Group.id == user_group.group_id)
        .options(
        joinedload(Group.courses).joinedload(GroupsCourses.course)))
    group = query.scalars().first()
    courses_dto = list(map(lambda t: CourseDto.from_orm(t.course), group.courses))
    return CoursesResponse(courses=courses_dto)


@router.get("/get_one", response_model=CourseResponse)
async def get_courses(group_id: int,
                      course_id: int,
                      current_user: User = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)) -> CourseResponse:
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
                                  .where(GroupsCourses.group_id == group_id)
                                  .where(GroupsCourses.course_id == course_id)
                                  .options(joinedload(GroupsCourses.course)))
    group_course = query.scalars().first()
    return CourseResponse.from_orm(group_course.course)
