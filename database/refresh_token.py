from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref

from database import Base


class RefreshToken(Base):
    __tablename__ = "dbo_refresh_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(200))
    user_id = Column(Integer, ForeignKey("dbo_user.id"))
    user = relationship("User", back_populates="refresh_token")
