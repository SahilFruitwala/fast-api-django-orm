from datetime import datetime
from decimal import Decimal
from typing import Annotated

from django.db.models import QuerySet
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, BeforeValidator, Field  # For request/response models

from db_app.models import Transaction as TransactionModel
from enums import TransactionTypeEnum

router = APIRouter(
    prefix='/transactions',
    tags=['transactions'],
    responses={404: {'description': 'Not found'}},
)


def valid_transaction_type(transaction_type: str) -> str:
    if not transaction_type.strip() or transaction_type.strip() not in TransactionTypeEnum:
        raise ValueError('Invalid transaction type.')
    return transaction_type


class TransactionBase(BaseModel):
    date: datetime
    amount: Decimal
    description: str
    transaction_type: Annotated[str, BeforeValidator(valid_transaction_type)]


class TransactionCreate(BaseModel):
    transaction_type: Annotated[str, BeforeValidator(valid_transaction_type)]
    amount: Decimal
    description: str | None = None
    date: datetime = Field(default=datetime.now())
    account_id: int
    from_account: int | None = None


class TransactionUpdate(BaseModel):
    transaction_type: Annotated[str, BeforeValidator(valid_transaction_type)] | None = None
    amount: Decimal | None = None
    description: str | None = None
    date: datetime | None = None
    from_account: int | None = None
    account_id: int


class Transaction(TransactionBase):  # For response model
    id: int

    class ConfigDict:
        from_attributes = True  # Pydantic V2+


# Read All
def get_all_transactions_db(user_id: int) -> list[TransactionModel]:
    # .all() is lazy, convert to list to execute the query
    return TransactionModel.objects.filter(user_id=user_id)


# Create
def create_transaction_db(user_id: int, transaction_data: TransactionCreate) -> TransactionModel:
    return TransactionModel.objects.create(user_id=user_id, **transaction_data.model_dump(exclude_none=True))


# Read One
def get_transaction_db(transaction_id: int, user_id: int) -> QuerySet[TransactionModel]:
    transaction = TransactionModel.objects.filter(id=transaction_id, user_id=user_id)
    if not transaction.first():
        raise HTTPException(status_code=404, detail='Transaction does not found.')
    return transaction


# Update
def update_transaction_db(transaction_id: int, user_id: int, transaction_data: TransactionUpdate) -> TransactionModel:
    existing_transaction = get_transaction_db(transaction_id, user_id=user_id)
    existing_transaction.update(**transaction_data.model_dump(exclude_none=True, exclude={'user_id', 'id'}))

    return existing_transaction.first()


# Delete
def delete_transaction_db(transaction_id: int, user_id: int):
    transaction = get_transaction_db(transaction_id, user_id)
    transaction.delete()
    return True  # Indicate success


@router.get('/', response_model=list[Transaction])
def read_transactions(user_id: int = Query(...)):
    """Retrieve all transactions from the database."""
    return get_all_transactions_db(user_id)


@router.post('/', response_model=Transaction, status_code=201)
def create_transaction(transaction_data: TransactionCreate, user_id: int = Query(...)):
    """Create a new transaction in the database."""
    return create_transaction_db(user_id, transaction_data)


@router.get('/{transaction_id}', response_model=Transaction)
def read_transaction(transaction_id: int, user_id: int = Query(...)):
    """Retrieve a specific transaction by its ID."""
    return get_transaction_db(transaction_id, user_id).first()


@router.put('/{transaction_id}', response_model=Transaction)
def update_transaction(transaction_id: int, transaction_data: TransactionUpdate, user_id: int = Query(...)):
    """Update an existing transaction by its ID."""
    return update_transaction_db(transaction_id, user_id, transaction_data)


@router.delete('/{transaction_id}', status_code=204)  # 204 No Content on success
def delete_transaction(transaction_id: int, user_id: int = Query(...)):
    """Delete an transaction by its ID."""
    return delete_transaction_db(transaction_id, user_id)
