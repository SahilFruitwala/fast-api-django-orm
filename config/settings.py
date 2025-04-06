import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to project root

# Load .env file variables (optional for SQLite default, but good practice)
load_dotenv(BASE_DIR / '.env')

# Secret key (still needed by Django)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-orm-only')

# Debug setting
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Define apps that contain your models
INSTALLED_APPS = [
    'db_app',  # Your app containing models (created later)
]

# --- Database Configuration for SQLite ---
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# Default to SQLite for simplicity if no .env is found

_db_engine = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
_db_name = os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3')  # Or ':memory:'

_test_db_name = os.getenv('TEST_DB_NAME', BASE_DIR / 'test_db.sqlite3')  # File path

DATABASES = {
    'default': {
        'ENGINE': _db_engine,
        'NAME': _db_name,  # Development DB name
        # Following are ignored by SQLite but needed for others like PostgreSQL
        'USER': os.getenv('TEST_DB_USER', os.getenv('DB_USER')),
        'PASSWORD': os.getenv('TEST_DB_PASSWORD', os.getenv('DB_PASSWORD')),
        'HOST': os.getenv('TEST_DB_HOST', os.getenv('DB_HOST')),
        'PORT': os.getenv('TEST_DB_PORT', os.getenv('DB_PORT')),
        'OPTIONS': {
            # Timeout in seconds (e.g., 15-30 seconds)
            # Default is often low (e.g., 5 seconds)
            'timeout': 20,
        },
        'TEST': {
            # THIS IS THE KEY PART FOR PYTEST-DJANGO
            'NAME': _test_db_name,  # Use the file path for tests
            # Optionally add specific test options if needed
            # 'OPTIONS': {
            #     'timeout': 30, # Test-specific timeout if desired
            # },
        },
    }
}

# --- End SQLite Configuration ---

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Timezone settings (recommended)
USE_TZ = True
TIME_ZONE = 'UTC'
