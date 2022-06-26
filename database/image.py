import random

from sqlalchemy import Column, Integer, String, Float, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship, backref

from database import Base
from database.base_meta import SQLAlchemyBase


class Image(SQLAlchemyBase):
    __tablename__ = "dbo_image"

    id = Column(String, primary_key=True, default=lambda: str(random.getrandbits(128)))
    data = Column(LargeBinary, nullable=False)