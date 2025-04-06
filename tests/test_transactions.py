import pytest
from datetime import datetime
from decimal import Decimal

from db_app.models import Transaction
from enums import TransactionTypeEnum


@pytest.mark.django_db(transaction=True)
def test_read_transactions(client, test_transaction, test_user):
    response = client.get(f"/transactions/?user_id={test_user.id}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(tx["id"] == test_transaction.id for tx in data)


@pytest.mark.django_db(transaction=True)
def test_create_transaction(client, test_user, test_account):
    data = {
        "amount": "50.00",
        "description": "Lunch",
        "date": datetime.now().isoformat(),
        "account_id": test_account.id,
        "from_account": None,
        "transaction_type": TransactionTypeEnum.EXPENSE.value,
    }
    response = client.post(f"/transactions/?user_id={test_user.id}", json=data)
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["description"] == "Lunch"
    assert res_json["id"] is not None


def test_error(client, test_user, test_account):
    data = {
        "amount": "50.00",
        "description": "Lunch",
        "date": datetime.now().isoformat(),
        "account_id": test_account.id,
        "transaction_type": "Blah Blah",
    }
    response = client.post(f"/transactions/?user_id={test_user.id}", json=data)
    assert response.status_code == 422

    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid transaction type.'


@pytest.mark.django_db(transaction=True)
def test_read_transaction(client, test_transaction, test_user):
    response = client.get(f"/transactions/{test_transaction.id}?user_id={test_user.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_transaction.id


@pytest.mark.django_db(transaction=True)
def test_update_transaction(client, test_transaction, test_user, test_account):
    updated_data = {
        "description": "Updated Transaction",
        "date": datetime.now().isoformat(),
        "account_id": test_account.id,
        "from_account": None
    }
    response = client.put(
        f"/transactions/{test_transaction.id}?user_id={test_user.id}",
        json=updated_data,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated Transaction"


@pytest.mark.django_db(transaction=True)
def test_delete_transaction(client, test_transaction, test_user):
    response = client.delete(f"/transactions/{test_transaction.id}?user_id={test_user.id}")
    assert response.status_code == 204
    assert not Transaction.objects.filter(id=test_transaction.id).exists()


@pytest.mark.django_db(transaction=True)
def test_read_nonexistent_transaction(client, test_user):
    response = client.get(f"/transactions/99999?user_id={test_user.id}")
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_update_nonexistent_transaction(client, test_user, test_account):
    data = {
        "description": "Nonexistent",
        "date": datetime.now().isoformat(),
        "account_id": test_account.id,
        "from_account": None
    }
    response = client.put(f"/transactions/99999?user_id={test_user.id}", json=data)
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_delete_nonexistent_transaction(client, test_user):
    response = client.delete(f"/transactions/99999?user_id={test_user.id}")
    assert response.status_code == 404
