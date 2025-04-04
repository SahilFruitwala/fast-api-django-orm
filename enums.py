from enum import Enum


class AccountTypeEnum(Enum):
    CHECKING = 'Checking Account'
    SAVINGS = 'Savings Account'
    CREDIT_CARD = 'Credit Card'
    INVESTMENT = 'Investment Account'
    CASH = 'Cash'
    OTHER = 'Other'


class CategoryEnum(Enum):
    INCOME = 'Income'
    EXPENSE = 'Expense'


class TransactionTypeEnum(Enum):
    INCOME = 'Income'
    EXPENSE = 'Expense'
    TRANSFER = 'Transfer'
