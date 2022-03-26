from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service import get_admin, get_password_hash
from database import User, Admin, get_session


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post("/change_user_password")
async def change_user_password(user_id: int,
                               new_password: str,
                               current_user: User = Depends(get_admin),
                               session: AsyncSession = Depends(get_session)):
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {user_id} not found")
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Need to use /user/change_password to change password yourself")
    db_admin = await session.get(Admin, user_id)
    if db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"You can not change password to other admins")
    db_user.password = get_password_hash(new_password)
    await session.commit()
    return {"status": "Ok"}
