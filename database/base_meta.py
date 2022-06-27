from typing import AsyncIterator

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update

from config import DATABASE_URL, SQL_ECHO
import database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

engine = create_async_engine(DATABASE_URL, future=True, echo=SQL_ECHO)
Base = declarative_base()
metadata = Base.metadata
async_session_factory = sessionmaker(engine,
                                     expire_on_commit=False,
                                     class_=AsyncSession)


async def initialize_database():
    #async with engine.begin() as database_connection:
        # await database_connection.run_sync(metadata.drop_all)
        # await database_connection.run_sync(metadata.create_all)
    pass


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


class SQLAlchemyAdditional:
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def update_by_pydantic(self, model: BaseModel):
        self.update(**model.dict())





