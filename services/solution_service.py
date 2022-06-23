from typing import List, Tuple

from sqlalchemy import func, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import Solution
from database.solution import SolutionStatus


class SolutionService:
    @staticmethod
    async def get_best_solutions(group_id: int,
                                 course_id: int,
                                 task_id: int,
                                 session: AsyncSession) -> List[Solution]:
        row_column = func.row_number() \
            .over(partition_by=Solution.user_id,
                  order_by=(desc(Solution.status), desc(Solution.time_start), desc(Solution.score))) \
            .label('row_number')
        q = select(Solution, row_column) \
            .select_from(Solution) \
            .where(Solution.group_id == group_id,
                   Solution.course_id == course_id,
                   Solution.task_id == task_id) \
            .order_by(Solution.time_start.asc())
        query = await session.execute(q)
        solutions = list(map(lambda s: s[0], filter(lambda t: t[1] == 1, query.fetchall())))
        return solutions

    @staticmethod
    async def get_user_solution_on_review(group_id: int,
                                          course_id: int,
                                          task_id: int,
                                          user_id: int,
                                          session: AsyncSession) -> Solution:
        q = select(Solution) \
            .where(Solution.group_id == group_id,
                   Solution.course_id == course_id,
                   Solution.task_id == task_id,
                   Solution.user_id == user_id,
                   Solution.status == SolutionStatus.ON_REVIEW)
        query = await session.execute(q)
        solution_on_review = query.scalars().first()
        return solution_on_review

    @staticmethod
    async def get_best_user_solution(group_id: int,
                                     course_id: int,
                                     task_id: int,
                                     user_id: int,
                                     session: AsyncSession) -> Solution:
        q = select(Solution) \
            .where(Solution.group_id == group_id,
                   Solution.course_id == course_id,
                   Solution.task_id == task_id,
                   Solution.user_id == user_id) \
            .order_by(Solution.status.desc(),
                      Solution.score.desc(),
                      Solution.time_start.desc())
        query = await session.execute(q)
        solution = query.scalars().first()
        return solution

    @staticmethod
    async def get_solution(group_id: int,
                           course_id: int,
                           task_id: int,
                           solution_id: int,

                           user_id: int,
                           session: AsyncSession) -> Solution:
        q = select(Solution) \
            .where(Solution.group_id == group_id,
                   Solution.course_id == course_id,
                   Solution.task_id == task_id,
                   Solution.user_id == user_id,
                   Solution.id == solution_id)
        query = await session.execute(q)
        solution = query.scalars().first()
        return solution

    @staticmethod
    async def get_solution_by_id(solution_id: int,
                                 session: AsyncSession) -> Solution:
        query = await session.execute(select(Solution)
                                      .where(Solution.id == solution_id)
                                      .options(joinedload(Solution.task)))
        solution = query.scalars().first()
        return solution
