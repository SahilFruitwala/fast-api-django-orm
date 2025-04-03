from datetime import datetime
import os
import django
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field # For request/response models
from contextlib import asynccontextmanager
from typing import List, Optional

# --- Django ORM Setup ---
# Point to the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# Setup Django
django.setup()

# --- IMPORTANT: Import models *after* django.setup() ---
from db_app.models import User as UserModel # Rename to avoid Pydantic clash
from asgiref.sync import sync_to_async # To run sync ORM code in async context

# --- Pydantic Models (for API input/output validation) ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    pass # Inherits all fields from UserBase

class User(UserBase): # For response model
    id: int
    created_at: Optional[datetime] = None # Allow None if not always present/needed

    class Config:
        # Allow ORM objects to be used directly
        # Deprecated in Pydantic V2, use from_attributes=True
        # orm_mode = True
        from_attributes = True # Pydantic V2+


# --- FastAPI Application Setup ---

# Define lifespan manager for potential startup/shutdown logic (optional here)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    # You could put database connection pool setup here if not using Django's default handling
    yield
    print("Application shutdown...")
    # Clean up resources if needed

app = FastAPI(lifespan=lifespan)

# --- Asynchronous ORM Wrappers ---
# Use sync_to_async to wrap synchronous Django ORM calls

# Read All
async def get_all_users_db():
    # .all() is lazy, convert to list to execute the query
    users = await sync_to_async(list)(UserModel.objects.all())
    return users

# Create
async def create_user_db(user_data: UserCreate):
    user = await sync_to_async(UserModel.objects.create)(**user_data.model_dump())
    return user

# Read One
async def get_user_db(user_id: int):
    try:
        user = await sync_to_async(UserModel.objects.get)(pk=user_id)
        return user
    except UserModel.DoesNotExist:
        return None

# Update (example - adjust fields as needed)
async def update_user_db(user_id: int, user_data: UserCreate):
    user = await get_user_db(user_id)
    if not user:
        return None
    # Update fields
    user.name = user_data.name
    user.email = user_data.email
    await sync_to_async(user.save)() # Pass specific fields to update for efficiency if needed
    return user

# Delete
async def delete_user_db(user_id: int):
    user = await get_user_db(user_id)
    if not user:
        return False # Indicate not found
    await sync_to_async(user.delete)()
    return True # Indicate success

# --- API Endpoints ---

@app.post("/users/", response_model=User, status_code=201)
async def create_user(user_in: UserCreate):
    """
    Create a new User in the database.
    """
    new_user = await create_user_db(user_in)
    return new_user

@app.get("/users/", response_model=List[User])
async def read_users():
    """
    Retrieve all users from the database.
    """
    users = await get_all_users_db()
    return users

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    """
    Retrieve a specific User by its ID.
    """
    user = await get_user_db(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_in: UserCreate):
    """
    Update an existing User by its ID.
    """
    updated_user = await update_user_db(user_id, user_in)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", status_code=204) # 204 No Content on success
async def delete_user(user_id: int):
    """
    Delete an User by its ID.
    """
    success = await delete_user_db(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    # No content to return on successful deletion
    return None # Or return Response(status_code=204)


@app.get("/")
async def root():
    return {"message": "FastAPI with Django ORM is running!"}

