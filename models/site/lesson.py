from typing import List

from pydantic import BaseModel

from models.pydantic_sqlalchemy_core import LessonDto
from services.common import exclude_field, make_field_non_required, make_fields_non_required


class LessonsResponse(BaseModel):
    lessons: List[LessonDto]


class LessonResponse(LessonDto):
    pass


class LessonRequest(LessonDto):
    pass


@exclude_field("id")
class LessonPostRequest(LessonDto):
    pass


if __name__ == "__main__":
    print(*LessonPostRequest.__fields__.items(), sep='\n')
