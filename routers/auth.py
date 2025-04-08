from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from db_app.models import User as UserModel
from utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, is_correct_password

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {'description': 'Not found'}},
)


def authenticate_user(username: str, password: str) -> UserModel | bool:
    user = UserModel.objects.filter(email=username).first()
    if not user:
        return False
    if not is_correct_password(password, user.password):
        return False
    return user


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


@router.post('/login', response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'email': user.email, 'id': user.id}, expires_delta=access_token_expires)
    return Token(access_token=access_token)


