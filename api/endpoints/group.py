from typing import Optional, List

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.users_groups import UserGroupRole, UsersGroups
from models.pydantic_sqlalchemy_core import GroupDto
from models.site.group import GroupsResponse
from services.auth_service import get_current_active_user
from database import User, Group, get_session
from services.group_service import GroupService
from services.user_service import UserService
from services.users_groups_service import UsersGroupsService

router = APIRouter(
    prefix="/group",
    tags=["group"]
)


@router.get("/role", response_model=UserGroupRole)
async def get_role(group_id: int,
                   current_user: User = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)) -> UserGroupRole:
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    return user_group.role


@router.get("/get_all", response_model=GroupsResponse)
async def get_user_groups(current_user: User = Depends(get_current_active_user),
                          session: AsyncSession = Depends(get_session)) -> GroupsResponse:
    user_groups = await UsersGroupsService.get_user_groups(current_user.id,
                                                           session)
    groups = list(map(lambda t: t.group, user_groups))
    groups_dto = list(map(lambda t: GroupDto.from_orm(t), groups))
    return GroupsResponse(groups=sorted(groups_dto, key=lambda t: t.id))


@router.get("/{group_id}", response_model=GroupDto)
async def get_group(group_id: int,
                    current_user: User = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)) -> GroupDto:
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    group = await GroupService.get_group_by_id(group_id,
                                               session)
    return GroupDto.from_orm(group)


@router.put("/{group_id}", response_model=GroupDto)
async def put_group(group_id: int,
                    group_name: Optional[str] = None,  # TODO: to pydantic json validation fields
                    current_user: User = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)) -> GroupDto:
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    role = user_group.role
    group = await GroupService.get_group_by_id(group_id, session)
    current_user_is_admin = await UserService.is_admin(current_user.id, session)
    if current_user_is_admin or role == UserGroupRole.OWNER:
        if group_name:  # TODO: убрать деревенщину. Сделать на общий случай нормальные json
            group.name = group_name
        await session.commit()
        return GroupDto.from_orm(group)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")


@router.delete("/{group_id}", response_model=GroupDto)
async def delete_group(group_id: int,
                       current_user: User = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)):
    user_group = await UsersGroupsService.get_user_group(current_user.id,
                                                         group_id,
                                                         session)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    role = user_group.role
    group = await GroupService.get_group_by_id(group_id, session)
    current_user_is_admin = await UserService.is_admin(current_user.id, session)
    if current_user_is_admin or role == UserGroupRole.OWNER:
        await session.delete(group)
        await session.commit()
        # TODO: сделать response общим классом
        return {"detail": "ok"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")


@router.put("/", response_model=GroupDto)
async def put_group(group_name: int,
                    current_user: User = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)) -> GroupDto:
    current_user_is_admin_or_teacher = await UserService.is_admin_or_teacher(current_user.id, session)
    if current_user_is_admin_or_teacher:
        new_group = Group(name=group_name)
        session.add(new_group)
        await session.commit()
        return GroupDto.from_orm(Group)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to create group")
