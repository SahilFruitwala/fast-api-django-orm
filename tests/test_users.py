# tests/test_users.py
import pytest
from fastapi.testclient import TestClient  # Use sync client here too

from db_app.models import User  #
from utils import is_correct_password


@pytest.mark.django_db(transaction=True)
def test_create_user(client: TestClient):  # Use standard def, sync client
    """Test creating a new user."""
    # Use client.post directly (no await)
    response = client.post(
        '/users/',
        json={  #
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'newpassword123',
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'new@example.com'
    assert 'id' in data
    assert 'password' not in data

    # Verify user exists using synchronous ORM method
    user_exists = User.objects.filter(email='new@example.com').exists()  # Use sync .exists()
    assert user_exists


@pytest.mark.django_db(transaction=True)
def test_get_user(client: TestClient, test_user: User):  # Use standard def
    """Test retrieving a specific user."""
    # Use client.get directly
    response = client.get(f'/users/{test_user.id}')  #

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_user.id
    assert data['email'] == test_user.email
    assert data['name'] == test_user.name


@pytest.mark.django_db(transaction=True)
def test_get_all_users(client: TestClient, test_user: User):  # Use standard def
    """Test retrieving all users."""
    response = client.get('/users/')  #
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(u['id'] == test_user.id for u in data)


@pytest.mark.django_db(transaction=True)
def test_create_user_duplicate_email(client: TestClient, test_user: User):
    """Test creating a user with an email that already exists."""
    response = client.post(
        '/users/',
        json={
            'name': 'Another User',
            'email': test_user.email,  # Use existing user's email
            'password': 'newpassword123',
        },
    )
    assert response.status_code == 400  # Expecting Bad Request or similar error
    # Optional: check error detail if your endpoint provides specific messages
    # assert "Email already registered" in response.json().get("detail", "")


@pytest.mark.django_db(transaction=True)
def test_error_on_create(client):
    response = client.post(
        '/users/',
        json={  #
            'name': 'New User',
            'email': 'new@example.com',
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data['detail'][0]['msg'] == 'Value error, Password is required'

@pytest.mark.django_db(transaction=True)
def test_get_nonexistent_user(client: TestClient):
    """Test retrieving a user ID that does not exist."""
    non_existent_user_id = 99999
    response = client.get(f'/users/{non_existent_user_id}')
    assert response.status_code == 404  # Expecting Not Found


@pytest.mark.django_db(transaction=True)
def test_update_user_details(client: TestClient, test_user: User):
    """Test updating a user's name and email (no password change)."""
    update_data = {
        'name': 'Updated Test User Name',
        'email': 'updated.email@example.com',
        # No password fields included
    }
    response = client.put(f'/users/{test_user.id}', json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_user.id
    assert data['name'] == 'Updated Test User Name'
    assert data['email'] == 'updated.email@example.com'

    # Verify changes in DB
    test_user.refresh_from_db()
    assert test_user.name == 'Updated Test User Name'
    assert test_user.email == 'updated.email@example.com'


@pytest.mark.django_db(transaction=True)
def test_update_user_password(client: TestClient, test_user: User):
    """Test updating a user's password successfully."""
    original_plain_password = 'testpassword'  # The password used in the test_user fixture
    new_plain_password = 'newSecurePassword123'

    update_data = {
        'password': original_plain_password,  # Current password
        'new_password': new_plain_password,  # New password
        # Optional: can also update name/email here if desired
    }
    response = client.put(f'/users/{test_user.id}', json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_user.id  # Ensure user data is returned

    # Verify password change in DB by reloading user and checking password
    test_user.refresh_from_db()
    # Use your utility function to check the new password
    assert is_correct_password(new_plain_password, test_user.password)  #
    # Also check that the old password no longer works
    assert not is_correct_password(original_plain_password, test_user.password)  #


@pytest.mark.django_db(transaction=True)
def test_update_user_password_incorrect_current(client: TestClient, test_user: User):
    """Test updating password fails if current password is incorrect."""
    update_data = {
        'password': 'wrong_current_password',  # Incorrect current password
        'new_password': 'newSecurePassword123',
    }
    response = client.put(f'/users/{test_user.id}', json=update_data)
    assert response.status_code == 400  # Expect Bad Request
    assert 'Password does not match' in response.json().get('detail', '')


@pytest.mark.django_db(transaction=True)
def test_update_user_password_missing_current(client: TestClient, test_user: User):
    """Test updating password fails if current password is not provided."""
    update_data = {
        # "password": "testpassword", # Missing current password
        'new_password': 'newSecurePassword123'
    }
    response = client.put(f'/users/{test_user.id}', json=update_data)
    # Expecting 400 or 422 depending on Pydantic validation trigger
    assert response.status_code == 400 or response.status_code == 422
    # Check detail message if needed, e.g., "Password is required" from validator


@pytest.mark.django_db(transaction=True)
def test_update_user_not_found(client: TestClient):
    """Test updating a user that does not exist."""
    non_existent_user_id = 99999
    update_data = {'name': 'Wont Update'}
    response = client.put(f'/users/{non_existent_user_id}', json=update_data)
    assert response.status_code == 404  # Expecting Not Found from get_user_db


@pytest.mark.django_db(transaction=True)
def test_delete_user(client: TestClient, test_user: User):
    """Test deleting an existing user."""
    user_id_to_delete = test_user.id

    response = client.delete(f'/users/{user_id_to_delete}')
    # Expecting 204 No Content on successful deletion as per endpoint definition
    assert response.status_code == 204

    # Verify deletion in DB
    user_exists = User.objects.filter(id=user_id_to_delete).exists()
    assert not user_exists


@pytest.mark.django_db(transaction=True)
def test_delete_user_not_found(client: TestClient):
    """Test deleting a user that does not exist."""
    non_existent_user_id = 99999
    response = client.delete(f'/users/{non_existent_user_id}')
    assert response.status_code == 404  # Expecting Not Found from get_user_db
