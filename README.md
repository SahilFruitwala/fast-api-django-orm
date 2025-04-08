# FastAPI with Django ORM & JWT Authentication

## Description

This project demonstrates how to build a FastAPI application integrated with the Django ORM for database interactions, migrations, and model definitions. It uses basic email/password authentication secured with JSON Web Tokens (JWT). The setup allows defining Django models, managing database schema changes via migrations, and interacting with the database within FastAPI endpoints.

## Features

* **FastAPI:** Modern, high-performance web framework for building APIs.
* **Django ORM:** Mature and powerful Object-Relational Mapper for database interactions.
* **Django Migrations:** Robust system for managing database schema changes.
* **JWT Authentication:** Secure API endpoints using email/password login and JWT tokens.
* **Pydantic:** Data validation and settings management using Python type hints.
* **Async/Sync Compatibility:** Handles synchronous ORM calls within the async FastAPI environment.
* **Environment-Based Configuration:** Uses `.env` files for managing settings like database credentials and secret keys.
* **Modular Routers:** API endpoints organized into separate routers for users, accounts, transactions, and authentication.
* **Testing:** Includes tests using `pytest` and `TestClient`.

## Project Structure

* `main.py`: FastAPI application entry point.
* `config/`: Django project configuration.
    * `settings.py`: Django settings, reads `.env` file.
* `db_app/`: Django app containing database models and migrations.
    * `models.py`: Defines User, Account, Transaction, etc., models.
    * `migrations/`: Database migration files.
* `routers/`: FastAPI routers for different API resources.
    * `auth.py`: Handles user login and token generation.
    * `users.py`: User registration, profile management, password reset.
    * `accounts.py`: Account management endpoints.
    * `transactions.py`: Transaction management endpoints.
* `utils.py`: Utility functions, including password hashing and JWT creation/decoding.
* `enums.py`: Enumerations for choices like Account Type and Transaction Type.
* `manage.py`: Django's command-line utility for administrative tasks (like migrations).
* `tests/`: Contains Pytest tests for the API endpoints.
* `.env` (You need to create this): Stores environment variables.
* `requirements.txt` (You need to create this): Lists project dependencies.

## Prerequisites

* **Python:** Version 3.8+ recommended.
* **uv** (or pip): Python package installer.
* **Database System:** SQLite (default), PostgreSQL, or MySQL.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Create Virtual Environment:**
    ```bash
    # Using uv
    uv venv
    source .venv/bin/activate # Linux/macOS
    # .\.venv\Scripts\activate # Windows

    # Or using Python's built-in venv
    # python -m venv .venv
    # source .venv/bin/activate # Linux/macOS
    # .\.venv\Scripts\activate # Windows
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file listing all necessary packages (e.g., `fastapi`, `uvicorn[standard]`, `django`, `python-dotenv`, `bcrypt`, `PyJWT`, `passlib[bcrypt]`, `psycopg2-binary` (for PostgreSQL), `mysqlclient` (for MySQL), `pytest`, `httpx`). Then install:
    ```bash
    uv pip install -r requirements.txt
    # Or using pip
    # pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    * Create a `.env` file in the project root.
    * **Important:** Add `.env` to your `.gitignore` file to avoid committing sensitive information.
    * Populate `.env` with the following variables, adjusting values as needed:

    ```dotenv
    # --- Django Settings ---
    # Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    DJANGO_SECRET_KEY=your_django_secret_key
    DEBUG=True # Set to False in production

    # --- JWT Settings ---
    # Generate a strong secret (e.g., using openssl rand -hex 32)
    SECRET_KEY=your_jwt_secret_key
    ALGORITHM=HS256 # Or your chosen algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token validity duration in minutes

    # --- Database Configuration ---
    # Uncomment and configure ONE section based on your DB choice

    # Option 1: SQLite (Default)
    DB_ENGINE=django.db.backends.sqlite3
    DB_NAME=db.sqlite3 # Path relative to project root

    # Option 2: PostgreSQL (Requires psycopg2-binary)
    # DB_ENGINE=django.db.backends.postgresql
    # DB_NAME=your_postgres_db_name
    # DB_USER=your_postgres_user
    # DB_PASSWORD=your_postgres_password
    # DB_HOST=localhost # Or your DB host
    # DB_PORT=5432

    # Option 3: MySQL (Requires mysqlclient)
    # DB_ENGINE=django.db.backends.mysql
    # DB_NAME=your_mysql_db_name
    # DB_USER=your_mysql_user
    # DB_PASSWORD=your_mysql_password
    # DB_HOST=localhost # Or your DB host
    # DB_PORT=3306
    ```

5.  **Run Database Migrations:**
    Apply the database schema defined in `db_app/models.py`:
    ```bash
    python manage.py migrate
    ```
    *(If you modify `db_app/models.py` in the future, first create a new migration file with `python manage.py makemigrations db_app` before running `migrate`)*.

## Running the Application

Start the FastAPI development server using Uvicorn:
```bash
uvicorn main:app --reload