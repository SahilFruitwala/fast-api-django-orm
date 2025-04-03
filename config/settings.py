# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # Points to project root

# Load .env file variables (optional for SQLite default, but good practice)
load_dotenv(BASE_DIR / '.env')

# Secret key (still needed by Django)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-orm-only')

# Debug setting
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Define apps that contain your models
INSTALLED_APPS = [
    'db_app', # Your app containing models (created later)
]

# --- Database Configuration for SQLite ---
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# Default to SQLite for simplicity if no .env is found
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        # Following are ignored by SQLite but needed for others like PostgreSQL
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# --- End SQLite Configuration ---

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Timezone settings (recommended)
USE_TZ = True
TIME_ZONE = 'UTC'

