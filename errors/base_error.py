from pydantic import BaseModel


class BaseError(Exception):
    error: str
    error_description: str
