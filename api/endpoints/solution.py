from fastapi import Depends, APIRouter, HTTPException, status, UploadFile, File
from typing import Optional

from sqlalchemy import select, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.solution import SolutionStatus, Solution
from database.users_groups import UserGroupRole

from database import User, UsersGroups, CoursesLessons, get_session, GroupsCourses, LessonsTasks
from models.pydantic_sqlalchemy_core import SolutionDto
from models.site.solution import SolutionsCountResponse, SolutionResponse
from services.auth_service import get_current_active_user, get_admin
from services.courses_lessons_service import CoursesLessonsService
from services.groups_courses_serivce import GroupsCoursesService
from services.lessons_tasks_service import LessonsTasksService
from services.solution_service import SolutionService
from services.user_service import UserService
from services.users_groups_service import UsersGroupsService

router = APIRouter(
    prefix="/solution",
    tags=["solution"]
)


@router.get("/get_count", response_model=Optional[SolutionsCountResponse])
async def get_solution_count(group_id: int,
                             course_id: int,
                             task_id: int,
                             current_user: User = Depends(get_current_active_user),
                             session: AsyncSession = Depends(get_session)) -> Optional[SolutionsCountResponse]:
    user_groups = await UsersGroupsService.get_group_users(group_id, session)
    solutions_count = len(user_groups)

    solutions = await SolutionService.get_best_solutions(group_id, course_id, task_id, session)

    solutions_complete_count = len(list(filter(lambda sol: sol.status == SolutionStatus.COMPLETE, solutions)))
    solutions_complete_not_max_count = len(
        list(filter(lambda sol: sol.status == SolutionStatus.COMPLETE_NOT_MAX, solutions)))
    solutions_complete_error_count = len(list(filter(lambda sol: sol.status == SolutionStatus.ERROR, solutions)))
    solutions_complete_on_review_count = len(
        list(filter(lambda sol: sol.status == SolutionStatus.ON_REVIEW, solutions)))
    solutions_undefined_count = solutions_count \
                                - solutions_complete_count \
                                - solutions_complete_not_max_count \
                                - solutions_complete_error_count \
                                - solutions_complete_on_review_count

    return SolutionsCountResponse(solutions_count=solutions_count,
                                  solutions_complete_count=solutions_complete_count,
                                  solutions_complete_not_max_count=solutions_complete_not_max_count,
                                  solutions_complete_error_count=solutions_complete_error_count,
                                  solutions_complete_on_review_count=solutions_complete_on_review_count,
                                  solutions_undefined_count=solutions_undefined_count)


@router.get("/get_best", response_model=Optional[SolutionResponse])
async def get_solution_best(group_id: int,
                            course_id: int,
                            task_id: int,
                            user_id: Optional[int] = None,
                            current_user: User = Depends(get_current_active_user),
                            session: AsyncSession = Depends(get_session)) -> Optional[SolutionResponse]:
    solution_on_review = await SolutionService.get_user_solution_on_review(group_id,
                                                                           course_id,
                                                                           task_id,
                                                                           (user_id if user_id else current_user.id),
                                                                           session)
    if solution_on_review:
        return SolutionResponse.from_orm(solution_on_review)

    solution = await SolutionService.get_best_user_solution(group_id,
                                                            course_id,
                                                            task_id,
                                                            (user_id if user_id else current_user.id),
                                                            session)
    if solution:
        return SolutionResponse.from_orm(solution)
    else:
        return


@router.get("/get_one", response_model=Optional[SolutionResponse])
async def get_solution(group_id: int,
                       course_id: int,
                       task_id: int,
                       solution_id: int,
                       user_id: Optional[int] = None,
                       current_user: User = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)) -> Optional[SolutionResponse]:
    solution = await SolutionService.get_solution(group_id,
                                                  course_id,
                                                  task_id,
                                                  solution_id,
                                                  (user_id if user_id else current_user.id),
                                                  session)
    if solution:
        return SolutionResponse.from_orm(solution)
    else:
        return


@router.post("/change_score", response_model=SolutionResponse)
async def change_solution_score(solution_id: int,
                                new_score: Optional[int] = 0,
                                is_rework: bool = False,
                                current_user: User = Depends(get_current_active_user),
                                session: AsyncSession = Depends(get_session)):
    solution = await SolutionService.get_solution_by_id(solution_id, session)
    is_admin = UserService.is_admin(current_user.id,
                                    session)
    user_group = await UsersGroupsService.get_user_group(solution.user_id,
                                                         solution.group_id,
                                                         session)
    if not user_group and not is_admin and user_group.role == UserGroupRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to solution")
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


@router.post("/post_file", response_model=SolutionResponse)
async def post_solution(group_id: int,
                        course_id: int,
                        lesson_id: int,
                        task_id: int,
                        file: UploadFile = File(...),
                        current_user: User = Depends(get_current_active_user),
                        session: AsyncSession = Depends(get_session)):
    # check group access
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    group_course = await GroupsCoursesService.get_group_course(group_id,
                                                               course_id,
                                                               session)
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    course_lesson = await CoursesLessonsService.get_course_lesson(course_id,
                                                                  lesson_id,
                                                                  session)
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    lesson_task = await LessonsTasksService.get_lesson_task(lesson_id, task_id, session)
    if not lesson_task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to task")

    last_solution_on_review = await SolutionService.get_user_solution_on_review(group_id,
                                                                                course_id,
                                                                                task_id,
                                                                                current_user.id,
                                                                                session)
    # TODO: update running tests in background tasks
    last_solution_on_review.status = SolutionStatus.ERROR
    code = await file.read()
    solution = Solution(user_id=current_user.id,
                        group_id=group_id,
                        course_id=course_id,
                        task_id=task_id,
                        code=code.decode("utf-8"))
    session.add(solution)
    await session.commit()
    return SolutionResponse.from_orm(solution)


@router.post("/post_code", response_model=SolutionResponse)
async def post_solution(group_id: int,
                        course_id: int,
                        lesson_id: int,
                        task_id: int,
                        code: str,
                        current_user: User = Depends(get_current_active_user),
                        session: AsyncSession = Depends(get_session)):
    # check group access
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    group_course = await GroupsCoursesService.get_group_course(group_id,
                                                               course_id,
                                                               session)
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to course")
    course_lesson = await CoursesLessonsService.get_course_lesson(course_id,
                                                                  lesson_id,
                                                                  session)
    if not course_lesson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to lesson")
    lesson_task = await LessonsTasksService.get_lesson_task(lesson_id, task_id, session)
    if not lesson_task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to task")

    last_solution_on_review = await SolutionService.get_user_solution_on_review(group_id,
                                                                                course_id,
                                                                                task_id,
                                                                                current_user.id,
                                                                                session)
    # TODO: update running tests in background tasks
    last_solution_on_review.status = SolutionStatus.ERROR
    solution = Solution(user_id=current_user.id,
                        group_id=group_id,
                        course_id=course_id,
                        task_id=task_id,
                        code=code)
    session.add(solution)
    await session.commit()
    return SolutionResponse.from_orm(solution)


@router.delete("/")
async def delete_solution(solution_id: int,
                          current_user: User = Depends(get_admin),
                          session: AsyncSession = Depends(get_session)):
    solution = await SolutionService.get_solution_by_id(solution_id, session)
    await session.delete(solution)
    return {"detail": "ok"}
