from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel

from database.solution import SolutionStatus


class StudentsWithSolution(BaseModel):
    user_id: int
    score: int
    status: SolutionStatus
    time_start: datetime
    time_finish: Optional[datetime]
