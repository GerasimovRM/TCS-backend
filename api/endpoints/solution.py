from fastapi import Depends, APIRouter, HTTPException, status, UploadFile, File
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.solution import SolutionStatus, Solution
from database.users_groups import UserGroupRole

from database import User, UsersGroups, CoursesLessons, get_session, GroupsCourses, LessonsTasks
from models.pydantic_sqlalchemy_core import SolutionDto
from models.site.solution import SolutionsCountResponse, SolutionResponse
from services.auth_service import get_current_active_user


router = APIRouter(
    prefix="/solution",
    tags=["solution"]
)


@router.get("/get_count", response_model=SolutionsCountResponse)
async def get_solution_count(group_id: int,
                             course_id: int,
                             task_id: int,
                             current_user: User = Depends(get_current_active_user),
                             session: AsyncSession = Depends(get_session)) -> SolutionsCountResponse:
    q = select(UsersGroups) \
        .where(UsersGroups.group_id == group_id,
               UsersGroups.role == UserGroupRole.STUDENT)
    query = await session.execute(q)
    solutions_count = len(query.scalars().all())

    q = select(Solution) \
        .where(Solution.group_id == group_id,
               Solution.course_id == course_id,
               Solution.task_id == task_id,
               or_(Solution.status == SolutionStatus.COMPLETE,
                   Solution.status == SolutionStatus.COMPLETE_NOT_MAX))
    query = await session.execute(q)
    solutions_complete_count = len(query.scalars().all())
    return SolutionsCountResponse(solutions_count=solutions_count,
                                  solutions_solved_count=solutions_complete_count)


@router.get("/get_best", response_model=Optional[SolutionResponse])
async def get_solution_best(group_id: int,
                            course_id: int,
                            task_id: int,
                            user_id: Optional[int] = None,
                            current_user: User = Depends(get_current_active_user),
                            session: AsyncSession = Depends(get_session)) -> Optional[SolutionResponse]:
    q = select(Solution) \
        .where(Solution.group_id == group_id,
               Solution.course_id == course_id,
               Solution.task_id == task_id,
               Solution.user_id == (user_id if user_id else current_user.id)) \
        .order_by(Solution.score.desc(),
                  Solution.status.desc(),
                  Solution.time_start.desc())
    query = await session.execute(q)
    solution = query.scalars().first()
    if solution:
        return SolutionResponse.from_orm(solution)
    else:
        return


@router.get("/get_one", response_model=Optional[SolutionResponse])
async def get_solution(group_id: int,
                       course_id: int,
                       task_id: int,
                       solution_id: int,
                       current_user: User = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)) -> Optional[SolutionResponse]:
    q = select(Solution) \
        .where(Solution.group_id == group_id,
               Solution.course_id == course_id,
               Solution.task_id == task_id,
               Solution.user_id == current_user.id,
               Solution.id == solution_id)
    query = await session.execute(q)
    solution = query.scalars().first()
    if solution:
        return SolutionResponse.from_orm(solution)
    else:
        return


@router.post("/change_score", response_model=SolutionResponse)
async def change_solution_score(solution_id: int,
                                new_score: Optional[int],
                                is_rework: bool = False,
                                current_user: User = Depends(get_current_active_user),
                                session: AsyncSession = Depends(get_session)):
    # TODO: secure
    query = await session.execute(select(Solution)
                                  .where(Solution.id == solution_id)
                                  .options(joinedload(Solution.task)))
    solution = query.scalars().first()
    if is_rework or new_score == 0:
        solution.score = 0
        solution.status = SolutionStatus.ERROR
    else:
        solution.score = new_score
        if new_score == solution.task.max_score:
            solution.status = SolutionStatus.COMPLETE
        else:
            solution.status = SolutionStatus.COMPLETE_NOT_MAX
    await session.commit()
    return SolutionResponse.from_orm(solution)


@router.post("/post_one", response_model=SolutionResponse)
async def post_solution(group_id: int,
                        course_id: int,
                        lesson_id: int,
                        task_id: int,
                        file: UploadFile = File(...),
                        current_user: User = Depends(get_current_active_user),
                        session: AsyncSession = Depends(get_session)):
    # check group access
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id))

    user_group = query.scalars().first()
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    query = await session.execute(select(GroupsCourses)
                                  .where(GroupsCourses.group_id == group_id,
                                         GroupsCourses.course_id == course_id))
    # check course access
    group_course = query.scalars().first()
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    query = await session.execute(select(CoursesLessons)
                                  .where(CoursesLessons.course_id == course_id,
                                         CoursesLessons.lesson_id == lesson_id))
    # check lesson access
    course_lesson = query.scalars().first()
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    query = await session.execute(select(LessonsTasks)
                                  .where(LessonsTasks.task_id == task_id,
                                         LessonsTasks.lesson_id == lesson_id)
                                  .options(joinedload(LessonsTasks.task)))
    lesson_task = query.scalars().first()
    if not lesson_task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to task")

    query = await session.execute(select(Solution)
                                  .where(Solution.user_id == current_user.id,
                                         Solution.course_id == course_id,
                                         Solution.group_id == group_id,
                                         Solution.task_id == task_id,
                                         Solution.status == SolutionStatus.ON_REVIEW))
    on_review_solutions = query.scalars().all()
    for solution in on_review_solutions:
        solution.status = SolutionStatus.ERROR
    code = await file.read()
    solution = Solution(user_id=current_user.id,
                        group_id=group_id,
                        course_id=course_id,
                        task_id=task_id,
                        code=code.decode("utf-8"))
    session.add(solution)
    await session.commit()
    return SolutionResponse.from_orm(solution)
