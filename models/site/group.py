from typing import List

from pydantic import BaseModel

from models.pydantic_sqlalchemy_core import GroupDto


class GroupsResponse(BaseModel):
    groups: List[GroupDto]


class GroupResponse(GroupDto):
    pass
