from pydantic import BaseModel


# TODO: нахуя оно вообще в проекте?
class BaseError(BaseModel):
    error: str
    error_description: str
