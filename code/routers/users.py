from django.db.utils import IntegrityError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator  # For request/response models

from db_app.models import User as UserModel  # Rename to avoid Pydantic clash  # noqa: E402
from utils import get_hashed_password, is_correct_password  # noqa: E402

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
    password: str | None = None
    new_password: str | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values):
        password = values.get('password')
        new_password = values.get('new_password')
        if new_password and not password:
            raise ValueError('Password is required')

        return values


class User(UserBase):  # For response model
    id: int

    class ConfigDict:
        # Allow ORM objects to be used directly
        # Deprecated in Pydantic V2, use from_attributes=True
        # orm_mode = True
        from_attributes = True  # Pydantic V2+


# Read All
def get_all_users_db() -> list[UserModel]:
    # .all() is lazy, convert to list to execute the query
    users = UserModel.objects.all()
    return users


# Create
def create_user_db(user_data: UserCreate) -> UserModel:
    try:
        user = UserModel.objects.create(**user_data.model_dump())
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return user


# Read One
def get_user_db(user_id: int) -> UserModel:
    try:
        user = UserModel.objects.get(pk=user_id)
        return user
    except UserModel.DoesNotExist as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# Update
def update_user_db(user_id: int, user_data: UserUpdate) -> UserModel:
    existing_user = get_user_db(user_id)

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
def delete_user_db(user_id: int):
    user = get_user_db(user_id)
    user.delete()
    return True  # Indicate success


@router.get('/', response_model=list[User])
def read_users():
    """Retrieve all users from the database."""
    users = get_all_users_db()
    return users


@router.post('/', response_model=User, status_code=201)
def create_user(user_in: UserCreate):
    """Create a new User in the database."""
    new_user = create_user_db(user_in)
    return new_user


@router.get('/{user_id}', response_model=User)
def read_user(user_id: int):
    """Retrieve a specific User by its ID."""
    user = get_user_db(user_id)
    return user


@router.put('/{user_id}', response_model=User)
def update_user(user_id: int, user_data: UserUpdate):
    """Update an existing User by its ID."""
    updated_user = update_user_db(user_id, user_data)
    return updated_user


@router.delete('/{user_id}', status_code=204)  # 204 No Content on success
def delete_user(user_id: int):
    """Delete a User by its ID."""
    return delete_user_db(user_id)
