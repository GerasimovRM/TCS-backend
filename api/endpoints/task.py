from io import BytesIO
from typing import Optional, List, Union

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.responses import StreamingResponse

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import TaskDto
from models.site.group import GroupsResponse
from models.site.task import TasksResponse
from services.auth_service import get_current_active_user
from database import User, Group, get_session, GroupsCourses, CoursesLessons, Lesson, LessonsTasks, \
    Solution, Image, ChatMessage
from services.courses_lessons_service import CoursesLessonsService
from services.groups_courses_serivce import GroupsCoursesService
from services.lessons_tasks_service import LessonsTasksService
from services.users_groups_service import UsersGroupsService

router = APIRouter(
    prefix="/task",
    tags=["task"]
)


@router.get("/get_all",
            response_model=TasksResponse)
async def get_tasks(group_id: int,
                    course_id: int,
                    lesson_id: int,
                    current_user: User = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)) -> TasksResponse:
    # check group access
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    # check group access
    group_course = await GroupsCoursesService.get_group_course(group_id, course_id, session)
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    course_lesson = await CoursesLessonsService.get_course_lesson(course_id,
                                                                  lesson_id,
                                                                  session)
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    lesson_tasks = await LessonsTasksService.get_lesson_tasks(lesson_id, session)
    tasks_dto = list(map(lambda t: TaskDto.from_orm(t.task), lesson_tasks))
    return TasksResponse(tasks=tasks_dto)


@router.get("/get_one", response_model=TaskDto)
async def get_task(group_id: int,
                   course_id: int,
                   lesson_id: int,
                   task_id: int,
                   current_user: User = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)) -> TaskDto:
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
    course_lesson = await CoursesLessonsService.get_course_lesson(course_id,
                                                                  lesson_id,
                                                                  session)
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    lesson_task = await LessonsTasksService.get_lesson_task(lesson_id, task_id, session)
    if not lesson_task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to task")
    task_dto = TaskDto.from_orm(lesson_task.task)
    return task_dto


@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...),
                       session: AsyncSession = Depends(get_session)):
    data = await file.read()
    image = Image(data=data)
    session.add(image)
    await session.commit()


@router.get("/load_image")
async def load_image(image_id: Union[str, int],
                     session: AsyncSession = Depends(get_session)):
    query = await session.execute(select(Image)
                                  .where(Image.id == f"{image_id}"))
    image_db = query.scalars().first()
    if not image_db:
        return
    image_bytes = BytesIO(image_db.data)
    image_bytes.seek(0)
    return StreamingResponse(image_bytes, media_type="image/png")
