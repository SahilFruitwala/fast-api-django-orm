import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

load_dotenv('.env')

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def get_hashed_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def is_correct_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def create_access_token(data: dict[str, str | int], expires_delta: timedelta | None = None):
    expire = datetime.now(UTC) + (expires_delta if expires_delta else timedelta(minutes=15))
    data['exp'] = expire
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class Payload(BaseModel):
    id: int
    email: str
    exp: datetime | None = None


def decode_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> Payload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('email')
        if email is None:
            raise credentials_exception
        return Payload(**payload)
    except InvalidTokenError:
        raise credentials_exception
