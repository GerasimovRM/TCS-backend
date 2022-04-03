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
from services.auth_service import get_current_active_user, get_current_user, get_password_hash
from services.auth_service import verify_password

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/", response_model=UserDto)
async def get_user(user_id: int,
                   current_user: User = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)) -> UserDto:
    query = await session.execute(select(User)
                                  .where(User.id == user_id))
    user = query.scalars().first()
    return UserDto.from_orm(user)


@router.get("/students_with_solution", response_model=List[StudentsWithSolution])
async def get_students_solution(group_id: int,
                                course_id: int,
                                task_id: int,
                                current_user: User = Depends(get_current_active_user),
                                session: AsyncSession = Depends(get_session)) -> List[StudentsWithSolution]:
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id,
                                         UsersGroups.role != UserGroupRole.STUDENT))
    group_user = query.scalars().first()
    if not group_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    row_column = func.row_number() \
        .over(partition_by=Solution.user_id,
              order_by=(desc(Solution.score), desc(Solution.status))) \
        .label('row_number')
    q = select(Solution, row_column) \
        .select_from(Solution) \
        .where(Solution.group_id == group_id,
               Solution.course_id == course_id,
               Solution.task_id == task_id) \
        .order_by(Solution.time_start.asc())

    query = await session.execute(q)
    solutions = list(map(lambda s: s[0], filter(lambda t: t[1] == 1, query.fetchall())))

    return [StudentsWithSolution(user_id=solution.user_id,
                                 score=solution.score,
                                 time_start=solution.time_start,
                                 status=solution.status,
                                 time_finish=solution.time_finish) for solution in solutions]


@router.get("/students_group", response_model=List[UserDto])
async def get_students_group(group_id: int,
                             current_user: User = Depends(get_current_active_user),
                             session: AsyncSession = Depends(get_session)) -> List[UserDto]:
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id,
                                         UsersGroups.role != UserGroupRole.STUDENT))
    group_user = query.scalars().first()
    if not group_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")

    query = await session.execute(select(UsersGroups).join(UsersGroups.user)
                                  .where(UsersGroups.group_id == group_id,
                                         UsersGroups.role == UserGroupRole.STUDENT)
                                  .options(joinedload(UsersGroups.user))
                                  .order_by(User.last_name.asc()))
    group_users = query.scalars().all()
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
