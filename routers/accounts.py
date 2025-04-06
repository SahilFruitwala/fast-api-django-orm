from decimal import Decimal
from typing import Annotated

from django.db.models import QuerySet
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, BeforeValidator, Field  # For request/response models

from db_app.models import Account as AccountModel
from enums import AccountTypeEnum

router = APIRouter(
    prefix='/accounts',
    tags=['accounts'],
    responses={404: {'description': 'Not found'}},
)


def validated_account_type(account_type: str) -> str:
    if not account_type.strip() or account_type.strip() not in AccountTypeEnum:
        raise ValueError('Invalid account type.')
    return account_type


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    account_type: Annotated[str, BeforeValidator(validated_account_type)]
    balance: Decimal = 0
    description: str | None = ''


class AccountUpdate(BaseModel):
    name: str | None = None
    account_type: Annotated[str, BeforeValidator(validated_account_type)] | None = None
    balance: Decimal | None = None
    description: str | None = None


class Account(AccountBase):  # For response model
    id: int

    class ConfigDict:
        # Allow ORM objects to be used directly
        # Deprecated in Pydantic V2, use from_attributes=True
        # orm_mode = True
        from_attributes = True  # Pydantic V2+


# Read All
def get_all_accounts_db(user_id: int) -> list[AccountModel]:
    # .all() is lazy, convert to list to execute the query
    return AccountModel.objects.filter(user_id=user_id)


# Create
def create_account_db(user_id: int, account_data: AccountBase) -> AccountModel:
    return AccountModel.objects.create(user_id=user_id, **account_data.model_dump(exclude_none=True))


# Read One
def get_account_db(account_id: int, user_id: int) -> QuerySet[AccountModel]:
    account = AccountModel.objects.filter(id=account_id, user_id=user_id)
    if not account.first():
        raise HTTPException(status_code=404, detail='Account does not found.')
    return account


# Update
def update_account_db(account_id: int, user_id: int, account_data: AccountUpdate) -> AccountModel:
    existing_account = get_account_db(account_id, user_id=user_id)
    existing_account.update(**account_data.model_dump(exclude_none=True, exclude={'user_id', 'id'}))

    return existing_account.first()


# Delete
def delete_account_db(account_id: int, user_id: int):
    account = get_account_db(account_id, user_id)
    account.delete()
    return True  # Indicate success


@router.get('/', response_model=list[Account])
def read_accounts(user_id: int = Query(...)):
    """Retrieve all accounts from the database."""
    return get_all_accounts_db(user_id)


@router.post('/', response_model=Account, status_code=201)
def create_account(account_data: AccountBase, user_id: int = Query(...)):
    """Create a new Account in the database."""
    return create_account_db(user_id, account_data)


@router.get('/{account_id}', response_model=Account)
def read_account(account_id: int, user_id: int = Query(...)):
    """Retrieve a specific Account by its ID."""
    return get_account_db(account_id, user_id).first()


@router.put('/{account_id}', response_model=Account)
def update_account(account_id: int, account_data: AccountUpdate, user_id: int = Query(...)):
    """Update an existing Account by its ID."""
    return update_account_db(account_id, user_id, account_data)


@router.delete('/{account_id}', status_code=204)  # 204 No Content on success
def delete_account(account_id: int, user_id: int = Query(...)):
    """Delete an Account by its ID."""
    return delete_account_db(account_id, user_id)
