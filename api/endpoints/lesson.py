from typing import Optional, List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import LessonDto
from models.site.lesson import LessonsResponse, LessonResponse, LessonPostRequest
from services.auth_service import get_current_active_user, get_teacher_or_admin
from database import User, Group, get_session, GroupsCourses, Course, CoursesLessons, Lesson
from services.course_service import CourseService
from services.courses_lessons_service import CoursesLessonsService
from services.groups_courses_serivce import GroupsCoursesService
from services.lesson_service import LessonService
from services.users_groups_service import UsersGroupsService

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
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    group_course = await GroupsCoursesService.get_group_course(group_id,
                                                               course_id,
                                                               session)
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    course = await CourseService.get_course(course_id, session)
    course_lessons = await CoursesLessonsService.get_course_lessons(course_id, session)
    lessons_dto = list(map(lambda t: LessonDto.from_orm(t.lesson), course_lessons))
    return LessonsResponse(lessons=lessons_dto,
                           course_name=course.name,
                           course_description=course.description)


@router.get("/get_one", response_model=LessonResponse)
async def get_lesson(group_id: int,
                     course_id: int,
                     lesson_id: int,
                     current_user: User = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)) -> LessonResponse:
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    group_course = await GroupsCoursesService.get_group_course(group_id,
                                                               course_id,
                                                               session)
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")

    course_lesson = await CoursesLessonsService.get_course_lesson_with_lesson(course_id,
                                                                              lesson_id,
                                                                              session)
    return LessonResponse.from_orm(course_lesson.lesson)


@router.post("/", response_model=LessonResponse)
async def post_lesson(lesson_request: LessonPostRequest,
                      current_user=Depends(get_teacher_or_admin),
                      session: AsyncSession = Depends(get_session)) -> LessonResponse:
    lesson = Lesson(**lesson_request.dict())
    session.add(lesson)
    await session.commit()
    return LessonResponse.from_orm(lesson)


@router.put("/", response_model=LessonResponse)
async def put_lesson(lesson_request: LessonPostRequest,
                     current_user=Depends(get_teacher_or_admin),
                     session: AsyncSession = Depends(get_session)) -> LessonResponse:
    lesson = await LessonService.get_lesson(lesson_request.id, session)
    lesson.update_by_pydantic(lesson_request)
    await session.commit()
    return LessonResponse.from_orm(lesson)
