from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref

from database import Base


class Admin(Base):
    __tablename__ = "dbo_admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("dbo_user.id"))
    user = relationship("User", backref=backref("admin", uselist=False))
