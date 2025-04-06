from datetime import datetime
import os
from collections.abc import Generator  # No AsyncGenerator needed
from decimal import Decimal

import django
import pytest
from fastapi.testclient import TestClient  # Import the synchronous TestClient

from enums import TransactionTypeEnum

# --- Crucial: Set DJANGO_SETTINGS_MODULE early ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# Optionally force test DB settings via environment variables here if needed
# os.environ['USE_TEST_DB_IN_MEMORY'] = 'True' # Example

# --- Initialize Django ---
django.setup()

# --- Import your FastAPI app and models AFTER Django setup ---
from db_app.models import Account, User, Transaction  # noqa: E402
from main import app as fastapi_app  # noqa: E402
from utils import get_hashed_password  # noqa: E402


# --- Fixture for Sync Test Client ---
@pytest.fixture(scope='function')
def client() -> Generator[TestClient, None, None]:  # Use standard Generator
    """
    Provides a synchronous test client for making requests to the FastAPI app.
    """
    # TestClient is used directly, no 'async with' needed
    # The 'app' argument is correct for TestClient
    with TestClient(fastapi_app) as c:
        yield c


# --- Remove event_loop fixture as it's for asyncio ---
# @pytest.fixture(scope="session")
# def event_loop()... (REMOVE THIS)


# --- Database Fixtures (using pytest-django markers) ---
# These remain the same as they interact with Django ORM directly


@pytest.fixture(scope='function')
def test_user(db) -> User:  # `db` fixture provided by pytest-django  # noqa: ARG001
    """
    Creates a test user in the database before a test runs.
    """
    hashed_password = get_hashed_password('testpassword')  #
    user = User.objects.create(  # Use synchronous create
        name='Test User', email='test@example.com', password=hashed_password
    )  #
    return user


@pytest.fixture(scope='function')
def test_account(db, test_user: User) -> Account:  # noqa: ARG001
    """
    Creates a test account associated with the test_user.
    """
    account = Account.objects.create(  # Use synchronous create
        user=test_user,
        name='Test Checking',
        account_type='Checking Account',  # Use actual value from your choices
        balance='100.50',
    )  #
    return account

@pytest.fixture
def test_transaction(test_user, test_account):
    return Transaction.objects.create(
        user=test_user,
        account=test_account,
        date=datetime.now().date(),
        amount=Decimal('50.00'),
        description="Test Transaction",
        transaction_type=TransactionTypeEnum.EXPENSE.value,
    )
