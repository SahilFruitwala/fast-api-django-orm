# FastAPI with Django ORM Project

## Description

This project demonstrates how to build a FastAPI application that uses the powerful Django ORM for database interactions, migrations, and model definitions. It provides a foundation for building robust APIs leveraging asynchronous FastAPI with the synchronous capabilities of the Django ORM via `asgiref`.

This setup allows you to define Django models, run database migrations using `manage.py`, and interact with your database within FastAPI endpoints.

## Features

* **FastAPI:** Modern, fast (high-performance) web framework for building APIs.
* **Django ORM:** Mature and powerful Object-Relational Mapper for database interactions.
* **Django Migrations:** Robust system for managing database schema changes.
* **Pydantic:** Data validation and settings management using Python type hints.
* **UV:** Fast Python package installer and virtual environment manager.
* **Async/Sync Compatibility:** Uses `asgiref.sync.sync_to_async` (or FastAPI's built-in handling for `def` routes) to safely run synchronous ORM code in an async environment.
* **Environment-Based Configuration:** Uses `.env` files for easy and secure configuration.

## Prerequisites

Before you begin, ensure you have the following installed:

* **Python:** Version 3.8 or higher recommended.
* **uv:** The package installer. If you don't have it, install it (e.g., `pip install uv`).

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Create Virtual Environment:**
    Use `uv` to create and activate a virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # .\.venv\Scripts\activate  # Windows PowerShell
    ```

3.  **Install Dependencies:**
    Install all required packages using `uv`:
    ```bash
    # Base requirements (FastAPI, Django, Uvicorn, etc.)
    uv pip install fastapi "uvicorn[standard]" django python-dotenv asgiref

    # --- IMPORTANT: Install DATABASE DRIVER if NOT using SQLite ---
    # Example for PostgreSQL:
    # uv pip install psycopg2-binary
    # Example for MySQL:
    # uv pip install mysqlclient
    ```
    *Note: SQLite is used by default and does not require a separate driver installation.*

4.  **Configure Environment:**
    See the **Configuration** section below to set up your `.env` file.

5.  **Run Database Migrations:**
    Apply the initial database schema:
    ```bash
    python manage.py migrate
    ```
    *(If you define new models or change existing ones in `db_app/models.py`, you'll need to run `python manage.py makemigrations db_app` followed by `python manage.py migrate` again.)*

## Configuration

Application settings, especially sensitive ones like database credentials and the Django secret key, are managed via environment variables loaded from a `.env` file located in the project root.

1.  **Create `.env` File:**
    Copy the example file (`.env.example` if you create one, otherwise create it manually) to `.env`:
    ```bash
    cp .env.example .env
    ```
    *(If `.env.example` doesn't exist, create a new file named `.env`)*

    **IMPORTANT:** Add `.env` to your `.gitignore` file to prevent committing secrets to version control!

    ```gitignore
    # .gitignore
    .env
    .venv/
    db.sqlite3 # If using SQLite default name
    __pycache__/
    *.pyc
    ```

2.  **Edit `.env` File:**
    Open the `.env` file and modify the variables according to your environment and database choice. Here's a template and examples:

    ```dotenv
    # .env file

    # --- Core Django Setting ---
    # Generate a strong, unique secret key.
    # You can generate one using: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    DJANGO_SECRET_KEY=your_strong_random_secret_key_here_please_change

    # --- Development Setting ---
    # Set to True to enable debug mode (shows detailed error pages, etc.)
    # Should be False in production!
    # DEBUG=True

    # --- Database Configuration ---
    # Choose ONE of the following database configurations (or adapt as needed).
    # The settings are read by config/settings.py

    # Option 1: SQLite (Default if no DB variables are set)
    # Engine: django.db.backends.sqlite3
    # Creates a file named db.sqlite3 in the project root by default.
    # You usually DON'T need to set these explicitly for the default SQLite setup.
    # DB_ENGINE=django.db.backends.sqlite3
    # DB_NAME=db.sqlite3 # You can customize the filename here if desired

    # Option 2: PostgreSQL (Requires 'psycopg2-binary' or 'psycopg')
    # Uncomment and fill these if using PostgreSQL. Also install the driver.
    # DB_ENGINE=django.db.backends.postgresql
    # DB_NAME=your_postgres_db_name
    # DB_USER=your_postgres_user
    # DB_PASSWORD=your_postgres_password
    # DB_HOST=localhost # Or your DB host IP/domain
    # DB_PORT=5432      # Or your DB port

    # Option 3: MySQL (Requires 'mysqlclient')
    # Uncomment and fill these if using MySQL. Also install the driver.
    # DB_ENGINE=django.db.backends.mysql
    # DB_NAME=your_mysql_db_name
    # DB_USER=your_mysql_user
    # DB_PASSWORD=your_mysql_password
    # DB_HOST=localhost # Or your DB host IP/domain
    # DB_PORT=3306      # Or your DB port

    # --- Add other environment variables as needed by your application ---

    ```

3.  **How Configuration Works:**
    * The `config/settings.py` file attempts to load variables from the `.env` file using `python-dotenv`.
    * It then uses these environment variables (or provides defaults, like for SQLite) to configure the `DATABASES` and other Django settings required by the ORM.
    * You generally only need to modify the `.env` file for configuration changes, not `config/settings.py`.

## Database Migrations

Django's migration system is used to manage database schema changes based on the models defined in `db_app/models.py`.

* **Creating Migrations:** When you add or modify models in `db_app/models.py`, create a new migration file:
    ```bash
    python manage.py makemigrations db_app
    ```
* **Applying Migrations:** To apply pending migrations to your database (including the initial setup):
    ```bash
    python manage.py migrate
    ```

## Running the Application

Use `uvicorn` to run the FastAPI development server:

```bash
uvicorn main:app --reload
```

# FastAPI with Django ORM - cURL Commands

## 1. Create a User
```sh
curl -X POST "http://127.0.0.1:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{"username": "John Doe", "email": "johndoe@example.com", "password": "pass1"}'
```

## 2. Get All Users
```sh
curl -X GET "http://127.0.0.1:8000/users/" \
     -H "Accept: application/json"
```

## 3. Get a Specific User by ID
```sh
curl -X GET "http://127.0.0.1:8000/users/1" \
     -H "Accept: application/json"
```

## 4. Update a User by ID
```sh
curl -X PUT "http://127.0.0.1:8000/users/1" \
     -H "Content-Type: application/json" \
     -d '{"name": "John Updated", "email": "johnupdated@example.com"}'
```

## 5. Delete a User by ID
```sh
curl -X DELETE "http://127.0.0.1:8000/users/1"
```

## 6. Check if the API is Running
```sh
curl -X GET "http://127.0.0.1:8000/"
```

## 7. Handle Errors (Example: Get Non-Existent User)
```sh
curl -X GET "http://127.0.0.1:8000/users/999" \
     -H "Accept: application/json"
```

## 8. Response Examples
### Success Response (Create User)
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "johndoe@example.com",
  "created_at": "2025-04-03T12:00:00Z"
}
```

### Error Response (User Not Found)
```json
{
  "detail": "User not found"
}
```

> Gemini 2.5 helped me in this setup.
