from decimal import Decimal
from typing import Literal, Annotated

from django.db.utils import IntegrityError
from django.db.models import QuerySet
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, BeforeValidator  # For request/response models

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
    description: str


class AccountCreate(AccountBase):
    user_id: int


class AccountUpdate(BaseModel):
    name: str | None = None
    account_type: Annotated[str, BeforeValidator(validated_account_type)] | None = None
    balance: Decimal | None = None
    description: str | None = None
    user_id: int


class AccountAttributes(BaseModel):
    user_id: int
    name: str | None = None


class Account(AccountBase):  # For response model
    id: int

    class ConfigDict:
        # Allow ORM objects to be used directly
        # Deprecated in Pydantic V2, use from_attributes=True
        # orm_mode = True
        from_attributes = True  # Pydantic V2+


# Read All
def get_all_accounts_db(account_data: AccountAttributes) -> list[AccountModel]:
    # .all() is lazy, convert to list to execute the query
    filter_data = {'user_id': account_data.user_id}
    if account_data.name:
        filter_data['name__icontains'] = account_data.name
    return AccountModel.objects.filter(**filter_data)


# Create
def create_account_db(account_data: AccountCreate) -> AccountModel:
    try:
        account = AccountModel.objects.create(**account_data.model_dump(exclude_none=True))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return account


# Read One
def get_account_db(account_id: int, user_id: int) -> QuerySet[AccountModel]:
    account = AccountModel.objects.filter(id=account_id, user_id=user_id)
    if not account.first():
        raise HTTPException(status_code=404, detail='Account does not found.')
    return account


# Update
def update_account_db(account_id: int, account_data: AccountUpdate) -> AccountModel:
    existing_account = get_account_db(account_id, user_id=account_data.user_id)
    existing_account.update(**account_data.model_dump(exclude_none=True, exclude={'user_id', 'id'}))

    return existing_account.first()


# Delete
def delete_account_db(account_id: int, account_data: AccountAttributes):
    account = get_account_db(account_id, account_data.user_id)
    account.delete()
    return True  # Indicate success


@router.get('/', response_model=list[Account])
def read_accounts(account_data: AccountAttributes):
    """Retrieve all accounts from the database."""
    return get_all_accounts_db(account_data)


@router.post('/', response_model=Account, status_code=201)
def create_account(account_data: AccountCreate):
    """Create a new Account in the database."""
    return create_account_db(account_data)


@router.get('/{account_id}', response_model=Account)
def read_account(account_id: int, account_data: AccountAttributes):
    """Retrieve a specific Account by its ID."""
    return get_account_db(account_id, account_data.user_id).first()


@router.put('/{account_id}', response_model=Account)
def update_account(account_id: int, account_data: AccountUpdate):
    """Update an existing Account by its ID."""
    return update_account_db(account_id, account_data)


@router.delete('/{account_id}', status_code=204)  # 204 No Content on success
def delete_account(account_id: int, account_data: AccountAttributes):
    """Delete an Account by its ID."""
    return delete_account_db(account_id, account_data)
