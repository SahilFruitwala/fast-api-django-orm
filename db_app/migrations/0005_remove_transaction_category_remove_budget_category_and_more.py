# Generated by Django 5.2 on 2025-04-06 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_app', '0004_remove_user_salt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='category',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='category',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='db_app.account'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transfer_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='outgoing_transfers', to='db_app.account'),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
