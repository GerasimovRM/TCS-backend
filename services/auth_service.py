from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_session
from database.user import User, UserStatus
from database.admin import Admin
from database.teacher import Teacher
from database.refresh_token import RefreshToken
from config import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import Response

from models.site.token import TokenData
from services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def create_access_token_user(user: User, session: AsyncSession) -> str:
    jwt_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    query = await session.execute(select(User)
                                  .where(User.id == user.id)
                                  .options(joinedload(User.admin))
                                  .options(joinedload(User.teacher)))
    user = query.scalars().first()
    jwt_data = {"vk_id": user.vk_id, "is_admin": bool(user.admin), "is_teacher": bool(user.teacher)}
    jwt_token = create_jwt_token(data=jwt_data, expires_delta=jwt_token_expires)
    return jwt_token


# TODO: async session context
async def create_refresh_token_user(user: User,
                                    session: AsyncSession,
                                    refresh_token: Optional[str] = None) -> str:
    jwt_token = create_jwt_token(data={"vk_id": user.vk_id}, verify_exp=False)
    new_refresh_token = RefreshToken(token=jwt_token, user=user)
    if refresh_token:
        query = await session.execute(select(RefreshToken).where(RefreshToken.token == refresh_token,
                                                                 RefreshToken.user == user))
        old_refresh_token = query.scalars().first()
        if old_refresh_token:
            await session.delete(old_refresh_token)
            await session.commit()
    session.add(new_refresh_token)
    await session.commit()
    return jwt_token


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password) if plain_password else False


def get_password_hash(password):
    return pwd_context.hash(password)


# TODO: async context
async def get_user(vk_id: str, session: AsyncSession) -> Optional[User]:
    query = await session.execute(select(User).where(User.vk_id == vk_id))
    user = query.scalars().first()
    return user


async def authenticate_user(vk_id: str, password: str, session: AsyncSession) -> Optional[User]:
    user = await get_user(vk_id, session)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_jwt_token(data: dict,
                     expires_delta: Optional[timedelta] = None,
                     verify_exp: bool = True) -> str:
    to_encode = data.copy()
    if verify_exp:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)) -> User:
    print(session)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        vk_id: str = payload.get("vk_id")
        if vk_id is None:
            raise credentials_exception
        token_data = TokenData(vk_id=vk_id)
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data.vk_id, session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user),
                                  session: AsyncSession = Depends(get_session)) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def get_admin(current_user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> User:
    is_admin = await UserService.is_admin(current_user.id, session)
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin")
    return current_user


async def get_teacher(current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)) -> User:
    s = await session.execute(select(Teacher))
    res = s.scalars().first()
    return res


async def get_teacher_or_admin(current_user: User = Depends(get_current_active_user),
                               session: AsyncSession = Depends(get_session)) -> User:
    is_admin_or_teacher = await UserService.is_admin_or_teacher(current_user.id, session)
    if is_admin_or_teacher:
        return current_user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher or admin")


