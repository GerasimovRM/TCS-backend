from typing import List

from pydantic import BaseModel

from models.pydantic_sqlalchemy_core import CourseDto


class CoursesResponse(BaseModel):
    courses: List[CourseDto]


class CourseResponse(CourseDto):
    pass
