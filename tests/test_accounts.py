# tests/test_accounts.py
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient  # Use sync client

from db_app.models import Account, User  #
from utils import get_hashed_password

# REMOVE pytestmark = pytest.mark.asyncio


@pytest.mark.django_db(transaction=True)
def test_create_account(client: TestClient, test_user: User):  # Use standard def
    """Test creating a new account for a user."""
    account_data = {
        'name': 'My Savings',
        'account_type': 'Savings Account',
        'balance': '500.00',
        'description': 'Test savings account',
    }
    # Use client.post directly
    response = client.post('/accounts/', params={'user_id': test_user.id}, json=account_data)

    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'My Savings'
    assert data['account_type'] == 'Savings Account'
    assert Decimal(data['balance']) == Decimal('500.00')
    assert 'id' in data

    # Verify in DB using sync ORM method
    acc_exists = Account.objects.filter(user=test_user, name='My Savings').exists()  # Use sync .exists()
    assert acc_exists


@pytest.mark.django_db(transaction=True)
def test_invalid_account_type(client: TestClient, test_user: User):  # Use standard def
    """Test creating a new account for a user."""
    account_data = {
        'name': 'My Savings',
        'account_type': 'Random Account',
        'balance': '500.00',
        'description': 'Test savings account',
    }
    # Use client.post directly
    response = client.post('/accounts/', params={'user_id': test_user.id}, json=account_data)

    assert response.status_code == 422
    data = response.json()
    assert data['detail'][0]['msg'] == 'Value error, Invalid account type.'


@pytest.mark.django_db(transaction=True)
def test_get_account(client: TestClient, test_user: User, test_account: Account):  # Use standard def
    """Test retrieving a specific account."""
    # Use client.get directly
    response = client.get(f'/accounts/{test_account.id}', params={'user_id': test_user.id})

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_account.id
    assert data['name'] == test_account.name
    assert data['account_type'] == test_account.account_type


@pytest.mark.django_db(transaction=True)
def test_get_accounts_for_user(client: TestClient, test_user: User, test_account: Account):  # Use standard def
    """Test retrieving all accounts for a specific user."""
    response = client.get('/accounts/', params={'user_id': test_user.id})  #

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(acc['id'] == test_account.id for acc in data)


@pytest.mark.django_db(transaction=True)
def test_update_account(client: TestClient, test_user: User, test_account: Account):
    """Test updating an existing account."""
    update_data = {
        'name': 'Updated Savings Name',
        'account_type': test_account.account_type,  # Keep same type or change
        'balance': '1250.75',  # Update balance
        'description': 'Updated description',
    }
    response = client.put(
        f'/accounts/{test_account.id}',
        params={'user_id': test_user.id},  # Send user_id as query param
        json=update_data,  # Send update data in body
    )
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_account.id
    assert data['name'] == 'Updated Savings Name'
    assert Decimal(data['balance']) == Decimal('1250.75')
    assert data['description'] == 'Updated description'

    # Verify change in DB
    test_account.refresh_from_db()
    assert test_account.name == 'Updated Savings Name'
    assert test_account.balance == Decimal('1250.75')


@pytest.mark.django_db(transaction=True)
def test_delete_account(client: TestClient, test_user: User, test_account: Account):
    """Test deleting an existing account."""
    account_id_to_delete = test_account.id

    # NOTE: Based on routers/accounts.py, DELETE expects user_id via AccountAttributes.
    # This likely means passing it as a query parameter, similar to GET/PUT.
    # If DELETE is changed later to use `user_id: int = Query(...)`, this test remains valid.
    delete_params = {'user_id': test_user.id}

    response = client.delete(f'/accounts/{account_id_to_delete}', params=delete_params)
    assert response.status_code == 204  # Or 204 No Content if endpoint returns nothing
    # If status is 200, check response body if applicable
    # data = response.json()
    # assert data.get("message") == "Account deleted successfully" # Or similar

    # Verify deletion in DB
    account_exists = Account.objects.filter(id=account_id_to_delete).exists()
    assert not account_exists


@pytest.mark.django_db(transaction=True)
def test_get_account_not_found(client: TestClient, test_user: User):
    """Test retrieving an account ID that does not exist."""
    non_existent_account_id = 99999
    response = client.get(f'/accounts/{non_existent_account_id}', params={'user_id': test_user.id})
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_get_account_wrong_user(client: TestClient, test_user: User, test_account: Account):
    """Test retrieving an account belonging to a different user."""
    # Create a second user
    other_user = User.objects.create(
        name='Other User',
        email='other@example.com',
        password=get_hashed_password('otherpass'),  #
    )

    # Try to get test_account using other_user's ID
    response = client.get(
        f'/accounts/{test_account.id}',
        params={'user_id': other_user.id},  # Use wrong user ID
    )
    # Expecting 404 because the get_account_db likely filters by user_id too
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_update_account_not_found(client: TestClient, test_user: User):
    """Test updating an account ID that does not exist."""
    non_existent_account_id = 99999
    update_data = {'name': 'Wont Update', 'balance': '100'}
    response = client.put(f'/accounts/{non_existent_account_id}', params={'user_id': test_user.id}, json=update_data)
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_update_account_wrong_user(client: TestClient, test_user: User, test_account: Account):
    """Test updating an account belonging to a different user."""
    other_user = User.objects.create(
        name='Other User',
        email='other@example.com',
        password=get_hashed_password('otherpass'),  #
    )
    update_data = {'name': 'Wont Update', 'balance': '100'}

    # Try to update test_account using other_user's ID
    response = client.put(
        f'/accounts/{test_account.id}',
        params={'user_id': other_user.id},  # Use wrong user ID
        json=update_data,
    )
    assert response.status_code == 404  # Expect 404 if update function checks user ownership


@pytest.mark.django_db(transaction=True)
def test_delete_account_not_found(client: TestClient, test_user: User):
    """Test deleting an account ID that does not exist."""
    non_existent_account_id = 99999
    response = client.delete(f'/accounts/{non_existent_account_id}', params={'user_id': test_user.id})
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_delete_account_wrong_user(client: TestClient, test_user: User, test_account: Account):
    """Test deleting an account belonging to a different user."""
    other_user = User.objects.create(
        name='Other User',
        email='other@example.com',
        password=get_hashed_password('otherpass'),  #
    )

    # Try to delete test_account using other_user's ID
    response = client.delete(
        f'/accounts/{test_account.id}',
        params={'user_id': other_user.id},  # Use wrong user ID
    )
    assert response.status_code == 404  # Expect 404 if delete function checks user ownership


@pytest.mark.django_db(transaction=True)
def test_get_all_accounts_for_user_empty(client: TestClient):
    """Test retrieving accounts for a user who has none."""
    # Create a user but no accounts for them
    user_with_no_accounts = User.objects.create(
        name='No Accounts User',
        email='noacc@example.com',
        password=get_hashed_password('noaccpass'),  #
    )
    response = client.get('/accounts/', params={'user_id': user_with_no_accounts.id})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
