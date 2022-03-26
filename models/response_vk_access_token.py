from pydantic import BaseModel


class ResponseVkAccessToken(BaseModel):
    access_token: str
    expires_in: int
    user_id: str
