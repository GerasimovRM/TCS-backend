from pydantic import BaseModel
from typing import Optional

from models.pydantic_sqlalchemy_core import UserDto


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenWithUserData(Token):
    user: UserDto


class TokenData(BaseModel):
    vk_id: Optional[str] = None
