from datetime import datetime, timedelta
from config import AuthConfig
from jwt import encode
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    return encoded_jwt
