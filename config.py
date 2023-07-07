from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()


class DBConfig:
    DB_USER = os.environ.get("POSTGRES_USER")
    DB_PASS = os.environ.get("POSTGRES_PASSWORD")
    DB_HOST = os.environ.get("POSTGRES_HOST")
    DB_PORT = os.environ.get("POSTGRES_PORT")
    DB_NAME = os.environ.get("POSTGRES_DB")
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


class AuthConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))


async def get_db():
    engine = create_async_engine(DBConfig.DB_URL, future=True)
    async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
