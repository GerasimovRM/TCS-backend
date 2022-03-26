from typing import Optional, List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import GroupDto
from models.site.group import GroupsResponse
from services.auth_service import get_current_active_user
from services.group_service import get_group_by_id
from database import User, Group, get_session

router = APIRouter(
    prefix="/group",
    tags=["group"]
)


@router.get("/role", response_model=UserGroupRole)
async def get_role(group_id: int,
                   current_user: User = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)) -> UserGroupRole:
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user,
                                         UsersGroups.group_id == group_id))
    user_group: UsersGroups = query.scalars().first()
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    return user_group.role


@router.get("/get_all", response_model=GroupsResponse)
async def get_groups(current_user: User = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)) -> GroupsResponse:
    query = await session.execute(select(UsersGroups)
                                  .where(UsersGroups.user == current_user)
                                  .options(joinedload(UsersGroups.group)))
    user_groups = query.scalars().all()
    groups = list(map(lambda t: t.group, user_groups))
    groups_dto = list(map(lambda t: GroupDto.from_orm(t), groups))
    return GroupsResponse(groups=groups_dto)


@router.get("/{group_id}", response_model=GroupDto)
async def get_group(group_id: int,
                    user: User = Depends(get_current_active_user)) -> GroupDto:
    group, role = get_group_by_id(group_id, user)
    return GroupDto.from_orm(group)


@router.post("/{group_id}", response_model=GroupDto)
async def post_group(group_id: int,
                     group_name: Optional[str] = None,
                     user: User = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)) -> GroupDto:
    group, role = get_group_by_id(group_id, user)
    if user.admin or role == UserGroupRole.OWNER:
        if group_name:
            group.name = group_name
        await session.commit()
        return GroupDto.from_orm(group)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")


@router.delete("/{group_id}", response_model=GroupDto)
async def delete_group(group_id: int,
                       user: User = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)):
    group, role = get_group_by_id(group_id, user)
    # TODO: проверить
    if user.admin or role == UserGroupRole.OWNER:
        await session.delete(group)
        await session.commit()
        # TODO: сделать request общим классом
        return {"detail": "ok"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")


@router.put("/", response_model=GroupDto)
async def put_group(group_name: int,
                    user: User = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)) -> GroupDto:
    # TODO: проверить
    if user.admin or user.teacher:
        new_group = Group(name=group_name)
        session.add(new_group)
        await session.commit()
        return GroupDto.from_orm(Group)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to create group")
