from typing import List

from pydantic import BaseModel

from models.pydantic_sqlalchemy_core import LessonDto
from common import exclude_field


class LessonsResponse(BaseModel):
    lessons: List[LessonDto]


class LessonResponse(LessonDto):
    pass


@exclude_field("id")
class LessonPostRequest(LessonDto):
    pass


if __name__ == "__main__":
    print(*LessonPostRequest.__fields__.items(), sep='\n')
