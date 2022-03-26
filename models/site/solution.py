from pydantic import BaseModel

from models.pydantic_sqlalchemy_core import SolutionDto


class SolutionResponse(SolutionDto):
    pass


class SolutionsCountResponse(BaseModel):
    solutions_count: int
    solutions_solved_count: int
