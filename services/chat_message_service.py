from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import ChatMessage


class ChatMessageService:
    @staticmethod
    async def get_chat_messages(group_id: int,
                                course_id: int,
                                task_id: int,
                                user_id: int,
                                session: AsyncSession) -> List[ChatMessage]:
        q = await session.execute(select(ChatMessage)
                                  .where(ChatMessage.group_id == group_id,
                                         ChatMessage.course_id == course_id,
                                         ChatMessage.task_id == task_id,
                                         ChatMessage.user_id == user_id))
        return q.scalars().all()
