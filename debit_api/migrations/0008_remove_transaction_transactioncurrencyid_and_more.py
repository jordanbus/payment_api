# Generated by Django 4.2.1 on 2023-05-15 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("debit_api", "0007_alter_transaction_transactiondate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="transactionCurrencyId",
        ),
        migrations.AddField(
            model_name="transaction",
            name="transactionCurrency",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="transactionCurrency",
                to="debit_api.currency",
            ),
            preserve_default=False,
        ),
    ]