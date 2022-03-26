from typing import Optional, Tuple

from fastapi import HTTPException, status

from database import User, Group
from database.users_groups import UserGroupRole, UsersGroups


def get_group_by_id(group_id: int, user: User) -> Tuple[Group, UserGroupRole]:
    user_group = next(filter(lambda t: t.group_id == group_id, user.groups), None)
    if not user_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad access to group")
    user_group: UsersGroups
    return user_group.group, user_group.role
