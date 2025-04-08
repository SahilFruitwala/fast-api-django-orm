from typing import Annotated

from django.db.utils import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator  # For request/response models

from db_app.models import User as UserModel  # Rename to avoid Pydantic clash  # noqa: E402
from utils import (
    Payload,
    decode_access_token,
    get_hashed_password,
    is_correct_password,
)  # noqa: E402

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {'description': 'Not found'}},
)


# --- Pydantic Models (for API input/output validation) ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: bytes

    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values):
        password = values.get('password')
        if not password:
            raise ValueError('Password is required')

        values['password'] = get_hashed_password(password)
        return values


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class ResetPasswordRequest(BaseModel):
    password: str
    new_password: str


class User(UserBase):  # For response model
    id: int

    class ConfigDict:
        from_attributes = True  # Pydantic V2+


# Create
def create_user_db(user_data: UserCreate) -> UserModel:
    try:
        user = UserModel.objects.create(**user_data.model_dump())
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return user


def get_user_from_email(email: str) -> UserModel:
    try:
        user = UserModel.objects.get(email=email)
        return user
    except UserModel.DoesNotExist as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# Update
def update_user_db(existing_user: UserModel, user_data: UserUpdate) -> UserModel:
    if user_data.new_password:
        if not is_correct_password(user_data.password, existing_user.password):
            raise HTTPException(status_code=400, detail='Password does not match.')
        new_password = get_hashed_password(user_data.new_password)
        existing_user.password = new_password

    existing_user.name = user_data.name or existing_user.name
    existing_user.email = user_data.email or existing_user.email
    existing_user.save()

    return existing_user


# Delete
def delete_user_db(user: UserModel):
    user.delete()
    return True


def get_current_user(payload: Annotated[Payload, Depends(decode_access_token)]) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    user = get_user_from_email(payload.email)
    if user is None:
        raise credentials_exception
    return user


@router.post('/', response_model=User, status_code=201)
def create_user(user_in: UserCreate):
    """Create a new User in the database."""
    new_user = create_user_db(user_in)
    return new_user


@router.get('/me', response_model=User)
def read_user(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Retrieve a specific User by its email."""
    return current_user


@router.patch('/', response_model=User)
def update_user(user_data: UserUpdate, current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Update an existing User by its ID."""
    updated_user = update_user_db(current_user, user_data)
    return updated_user


@router.delete('/', status_code=204)  # 204 No Content on success
def delete_user(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Delete a User by its ID."""
    return delete_user_db(current_user)
