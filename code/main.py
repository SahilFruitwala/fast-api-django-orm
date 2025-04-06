import os
from contextlib import asynccontextmanager

import django
from fastapi import FastAPI

# --- Django ORM Setup ---
# Point to the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# Setup Django
django.setup()

from routers.users import router as users_router  # noqa: E402
from routers.accounts import router as accounts_router  # noqa: E402


# --- FastAPI Application Setup ---
# Define lifespan manager for potential startup/shutdown logic (optional here)
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    print('Application startup...')
    # You could put database connection pool setup here if not using Django's default handling
    yield
    print('Application shutdown...')
    # Clean up resources if needed


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(accounts_router)


@app.get('/')
async def root():
    return {'message': 'FastAPI with Django ORM is running!'}
