from databases import DatabaseURL
from starlette.config import Config
from pathlib import Path
import os


config = Config(os.path.join(os.path.split(os.path.abspath(__file__))[0], ".env"))

VK_CLIENT_ID = config("VK_CLIENT_ID", cast=str)
VK_CLIENT_SECRET = config("VK_CLIENT_SECRET", cast=str)
VK_REDIRECT_URI = config("VK_REDIRECT_URI", cast=str)

SECRET_KEY = config("SECRET_KEY", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str)

SQL_ECHO = config("SQL_ECHO", cast=bool)
DATABASE_URL = config(
    "DATABASE_URL",
    cast=str)
DATABASE_URL = DATABASE_URL.replace("postgres", "postgresql+asyncpg", 1) + "?async_fallback=true"