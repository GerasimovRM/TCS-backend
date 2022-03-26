from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from database import Task
from database.base_meta import initialize_database, get_session
from models.site.token import Token
from services.auth_service import create_access_token_user, create_refresh_token_user, \
    authenticate_user
from api.endpoints import user_router, auth_router, group_router, admin_router,\
    course_router, lesson_router, solution_router, task_router, chat_message_router
"""
import logging
logger = logging.getLogger("databases")
logger.setLevel(logging.DEBUG)
"""
app = FastAPI(docs_url="/")
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(group_router)
app.include_router(lesson_router)
app.include_router(course_router)
app.include_router(solution_router)
app.include_router(task_router)
app.include_router(chat_message_router)


# app.state.database = database


@app.post("/token", response_model=Token)
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 refresh_token: Optional[str] = Cookie(None),
                                 session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_access_token = await create_access_token_user(user, session)
    jwt_refresh_token = await create_refresh_token_user(user, session, refresh_token)
    response.set_cookie("refresh_token", jwt_refresh_token, httponly=True)
    return Token(access_token=jwt_access_token)


@app.get("/test")
async def test(session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, 1)
    task.attachments = [
        {
            "attachment_type": 'input_output',
            "data": {
                "input": ['123', 'dfgdfg', 'bucks'],
                "output": ['bucks', 'dfgdfg', '123'],
            },
        },
        {
            "attachment_type": 'input_output',
            "data": {
                "input": ['112312323', 'dfasfasfgdfg', 'buasfsafcks'],
                "output": ['buck123213s', 'd123213213fgdfg', '123asdfsafd'],
            },
        },
        {
            "attachment_type": 'image',
            "data": {
                "url": 'https://avatars.githubusercontent.com/u/26022093?v=4',
            },
        },
    ]
    await session.commit()


@app.on_event("startup")
async def startup() -> None:
    await initialize_database()


@app.on_event("shutdown")
async def shutdown() -> None:
    # TODO: close connection
    pass


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tcs-fronend.web.app", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, log_level="info")
