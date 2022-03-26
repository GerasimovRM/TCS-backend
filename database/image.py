import random

from sqlalchemy import Column, Integer, String, Float, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship, backref

from database import Base


class Image(Base):
    __tablename__ = "dbo_image"

    id = Column(String, primary_key=True, default=lambda: str(random.getrandbits(128)))
    data = Column(LargeBinary, nullable=False)