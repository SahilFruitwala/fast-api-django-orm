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
    salt: bytes | None = None  # Optional field for salt
    
    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values):
        password = values.get('password')
        if not password:
            raise ValueError('Password is required')
        
        hashed_password, salt = get_hashed_password(password)
        values['password'] = hashed_password
        values['salt'] = salt
        return values


class User(UserBase):  # For response model
    id: int

    class Config:
        # Allow ORM objects to be used directly
        # Deprecated in Pydantic V2, use from_attributes=True
        # orm_mode = True
        from_attributes = True  # Pydantic V2+


# Read All
def get_all_users_db():
    # .all() is lazy, convert to list to execute the query
    users = UserModel.objects.all()
    return users


# Create
def create_user_db(user_data: UserCreate):
    try:
        user = UserModel.objects.create(**user_data.model_dump())
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return user


# Read One
def get_user_db(user_id: int):
    try:
        user = UserModel.objects.get(pk=user_id)
        return user
    except UserModel.DoesNotExist as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# Update (example - adjust fields as needed)
def update_user_db(user_id: int, user_data: UserCreate):
    user = get_user_db(user_id)
    # Update fields
    user.name = user_data.name
    user.email = user_data.email
    user.save()  # Pass specific fields to update for efficiency
    return user


# Delete
def delete_user_db(user_id: int):
    user = get_user_db(user_id)
    user.delete()
    return True  # Indicate success


@router.get('/', response_model=list[User])
def read_users():
    """
    Retrieve all users from the database.
    """
    users = get_all_users_db()
    return users


@router.post('/', response_model=User, status_code=201)
def create_user(user_in: UserCreate):
    """
    Create a new User in the database.
    """
    new_user = create_user_db(user_in)
    return new_user


@router.get('/{user_id}', response_model=User)
def read_user(user_id: int):
    """
    Retrieve a specific User by its ID.
    """
    user = get_user_db(user_id)
    return user


@router.put('/{user_id}', response_model=User)
def update_user(user_id: int, user_in: UserCreate):
    """
    Update an existing User by its ID.
    """
    updated_user = update_user_db(user_id, user_in)
    return updated_user


@router.delete('/{user_id}', status_code=204)  # 204 No Content on success
def delete_user(user_id: int):
    """
    Delete an User by its ID.
    """
    return delete_user_db(user_id)
