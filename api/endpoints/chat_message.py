from io import BytesIO
from typing import Optional, List, Union

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.responses import StreamingResponse

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import ChatMessageDto
from models.site.group import GroupsResponse
from models.site.task import TasksResponse
from services.auth_service import get_current_active_user
from services.group_service import get_group_by_id
from database import User, Group, get_session, GroupsCourses, CoursesLessons, Lesson, LessonsTasks, \
    Solution, Image, ChatMessage

router = APIRouter(
    prefix="/chat_message",
    tags=["chat_message"]
)


@router.get("/get_all", response_model=List[ChatMessageDto])
async def get_messages(group_id: int,
                       course_id: int,
                       task_id: int,
                       user_id: Optional[int] = None,
                       current_user=Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)) -> List[ChatMessageDto]:
    q = await session.execute(select(ChatMessage)
                              .where(ChatMessage.group_id == group_id,
                                     ChatMessage.course_id == course_id,
                                     ChatMessage.task_id == task_id,
                                     ChatMessage.user_id == (user_id if user_id else current_user.id)))
    return list(map(ChatMessageDto.from_orm, q.scalars().all()))


@router.post("/post_one")
async def post_message(group_id: int,
                       course_id: int,
                       task_id: int,
                       message_text: str,
                       user_id: Optional[int] = None,
                       current_user=Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)):
    cm = ChatMessage(task_id=task_id,
                     user_id=(user_id if user_id else current_user.id),
                     course_id=course_id,
                     group_id=group_id,
                     message_text=message_text,
                     from_id=current_user.id)
    session.add(cm)
    await session.commit()
    return ChatMessageDto.from_orm(cm)
