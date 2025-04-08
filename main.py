import os

import django
from fastapi import FastAPI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from routers.accounts import router as accounts_router  # noqa: E402
from routers.auth import router as auth_router  # noqa: E402
from routers.transactions import router as transactions_router  # noqa: E402
from routers.users import router as users_router  # noqa: E402

app = FastAPI(title='FastAPI + Django ORM')

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
