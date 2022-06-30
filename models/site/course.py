from typing import List

from pydantic import BaseModel

from models.pydantic_sqlalchemy_core import CourseDto
from services.common import exclude_field


class CoursesResponse(BaseModel):
    courses: List[CourseDto]


class CourseRequest(CourseDto):
    pass


@exclude_field("id")
class CoursePostRequest(CourseRequest):
    pass


class CoursePutRequest(CourseRequest):
    pass


class CourseResponse(CourseDto):
    pass
