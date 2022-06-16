from typing import List, Tuple

from sqlalchemy import func, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Solution


class SolutionService:
    @staticmethod
    async def get_last_solutions(group_id: int,
                                 course_id: int,
                                 task_id: int,
                                 session: AsyncSession) -> List[Tuple[Solution, int]]:
        row_column = func.row_number() \
            .over(partition_by=Solution.user_id,
                  order_by=(desc(Solution.score), desc(Solution.status), desc(Solution.time_start))) \
            .label('row_number')
        q = select(Solution, row_column) \
            .select_from(Solution) \
            .where(Solution.group_id == group_id,
                   Solution.course_id == course_id,
                   Solution.task_id == task_id) \
            .order_by(Solution.time_start.asc())
        query = await session.execute(q)
        return query.fetchall()
