from django.db import models

from enums import AccountTypeEnum, TransactionTypeEnum


class User(models.Model):
    """
    Represents a user in the system.
    """

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.BinaryField()  # Store hashed passwords
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Account(models.Model):
    """
    Represents a financial account, like a bank account, credit card, or investment account.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account_type = models.CharField(
        max_length=50,
        choices=[(tag.value, tag.name) for tag in AccountTypeEnum],
        default=AccountTypeEnum.CHECKING.value,
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    """
    Represents individual financial transactions.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name) for tag in TransactionTypeEnum],
        default=TransactionTypeEnum.EXPENSE.value,
    )
    transfer_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_transfers',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Budget(models.Model):
    """
    Represents a budget for a category.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
