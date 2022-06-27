from datetime import datetime
from enum import IntEnum

from sqlalchemy import Column, Integer, String, Float, ForeignKeyConstraint, Boolean, Enum, \
    DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.base_meta import Base, SQLAlchemyAdditional


class ChatMessage(Base, SQLAlchemyAdditional):
    __tablename__ = "dbo_chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(ForeignKey("dbo_task.id"))
    user_id = Column(ForeignKey("dbo_user.id"))
    course_id = Column(ForeignKey("dbo_course.id"))
    group_id = Column(ForeignKey("dbo_group.id"))

    message_text = Column(String(2000))
    from_id = Column(ForeignKey("dbo_user.id"))
    date = Column(DateTime, default=datetime.now)

    task = relationship("Task", back_populates="chat_messages")
    course = relationship("Course", back_populates="chat_messages")
    group = relationship("Group", back_populates="chat_messages")
    from_user = relationship("User", backref="chat_messages_from", foreign_keys=[from_id])
    user = relationship("User", backref="chat_messages", foreign_keys=[user_id])

