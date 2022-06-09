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
                                         CoursesLessons.lesson_id == lesson_id))
    # check group access
    course_lesson = query.scalars().first()
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    query = await session.execute(select(Lesson)
                                  .where(Lesson.id == course_lesson.lesson_id)
                                  .options(joinedload(Lesson.tasks)
                                           .joinedload(LessonsTasks.task)))
    lesson = query.scalars().first()
    tasks_dto = list(map(lambda t: TaskDto.from_orm(t.task), lesson.tasks))

    return TasksResponse(tasks=tasks_dto)


@router.get("/get_one", response_model=TaskDto)
async def get_task(group_id: int,
                   course_id: int,
                   lesson_id: int,
                   task_id: int,
                   current_user: User = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)) -> TaskDto:
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
    # check course access
    group_course = query.scalars().first()
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    query = await session.execute(select(CoursesLessons)
                                  .where(CoursesLessons.course_id == course_id,
                                         CoursesLessons.lesson_id == lesson_id))
    # check lesson access
    course_lesson = query.scalars().first()
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    query = await session.execute(select(LessonsTasks)
                                  .where(LessonsTasks.task_id == task_id,
                                         LessonsTasks.lesson_id == lesson_id)
                                  .options(joinedload(LessonsTasks.task)))
    lesson_task = query.scalars().first()
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
