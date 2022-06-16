from typing import Optional, List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import CourseDto
from models.site.course import CoursesResponse, CourseResponse
from services.auth_service import get_current_active_user
from database import User, Course, Group, get_session, GroupsCourses
from services.group_course_serivce import GroupCourseService
from services.group_service import GroupService
from services.users_groups_service import UsersGroupsService

router = APIRouter(
    prefix="/course",
    tags=["course"]
)


@router.get("/get_all", response_model=CoursesResponse)
async def get_courses(group_id: int,
                      current_user: User = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)) -> CoursesResponse:
    user_group = await UsersGroupsService.get_user_group(user_id=current_user.id,
                                                         group_id=group_id,
                                                         session=session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    group = await GroupService.get_group_by_id_with_courses(group_id, session)
    courses_dto = list(map(lambda t: CourseDto.from_orm(t.course), group.courses))
    return CoursesResponse(courses=courses_dto)


@router.get("/get_one", response_model=CourseResponse)
async def get_courses(group_id: int,
                      course_id: int,
                      current_user: User = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)) -> CourseResponse:
    # check group access
    user_group = await UsersGroupsService.get_user_group(user_id=current_user.id,
                                                         group_id=group_id,
                                                         session=session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    group_course = await GroupCourseService.get_group_course_with_courses(group_id, course_id, session)
    return CourseResponse.from_orm(group_course.course)
