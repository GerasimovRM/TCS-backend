from fastapi import Depends, APIRouter, HTTPException, status, Cookie
from typing import Optional, List, Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from database.users_groups import UserGroupRole
from database import User, Group, UsersGroups, Course, CoursesLessons, Lesson, get_session, \
    GroupsCourses, Solution
from models.pydantic_sqlalchemy_core import UserDto
from models.site.user import StudentsWithSolution
from services.auth_service import get_current_active_user, get_current_user, get_password_hash, \
    get_admin
from services.auth_service import verify_password
from services.solution_service import SolutionService
from services.user_service import UserService
from services.users_groups_service import UsersGroupsService

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/", response_model=UserDto)
async def get_user_by_id(user_id: int,
                         current_user: User = Depends(get_current_active_user),
                         session: AsyncSession = Depends(get_session)) -> UserDto:
    user = await UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found")
    return UserDto.from_orm(user)


@router.get("/students_with_solution", response_model=List[StudentsWithSolution])
async def get_students_solution(group_id: int,
                                course_id: int,
                                task_id: int,
                                current_user: User = Depends(get_current_active_user),
                                session: AsyncSession = Depends(get_session)) -> List[StudentsWithSolution]:
    group_user = await UsersGroupsService.get_user_group_teacher_or_admin(user_id=current_user.id,
                                                                          group_id=group_id,
                                                                          session=session)
    if not group_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    solutions = await SolutionService.get_best_solutions(group_id,
                                                         course_id,
                                                         task_id,
                                                         session)

    return [StudentsWithSolution(user_id=solution.user_id,
                                 score=solution.score,
                                 time_start=solution.time_start,
                                 status=solution.status,
                                 time_finish=solution.time_finish) for solution in solutions]


@router.get("/students_group", response_model=List[UserDto])
async def get_students_group(group_id: int,
                             current_user: User = Depends(get_current_active_user),
                             session: AsyncSession = Depends(get_session)) -> List[UserDto]:
    group_user = await UsersGroupsService.get_user_group_teacher_or_admin(user_id=current_user.id,
                                                                          group_id=group_id,
                                                                          session=session)
    if not group_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    group_users = await UsersGroupsService.get_group_users(group_id=group_id,
                                                           session=session)
    return list(map(UserDto.from_orm, map(lambda t: t.user, group_users)))


@router.post("/change_password/")
async def change_password(new_password: str,
                          current_password: Optional[str] = None,
                          current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    if not current_user.password and not current_password:
        current_user.password = get_password_hash(new_password)
    elif verify_password(current_password, current_user.password):
        current_user.password = get_password_hash(new_password)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong current password")
    await session.commit()
    return {"status": "Ok"}


@router.get("/get_data/", response_model=UserDto)
async def get_user_data(current_user: User = Depends(get_current_user)) -> UserDto:
    return UserDto.from_orm(current_user)


@router.post("/change_data", response_model=UserDto)
async def change_user_data(first_name: Optional[str] = None,
                           last_name: Optional[str] = None,
                           middle_name: Optional[str] = None,
                           avatar_url: Optional[str] = None,
                           current_user: User = Depends(get_current_active_user),
                           session: AsyncSession = Depends(get_session)):
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if middle_name:
        current_user.middle_name = middle_name
    if avatar_url:
        current_user.avatar_url = avatar_url
    await session.commit()
    return UserDto.from_orm(current_user)
