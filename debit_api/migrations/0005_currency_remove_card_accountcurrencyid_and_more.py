# Generated by Django 4.2.1 on 2023-05-13 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("debit_api", "0004_alter_card_cardnumber_alter_card_salt"),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                ("currencyId", models.AutoField(primary_key=True, serialize=False)),
                ("currencyName", models.CharField(max_length=50)),
                ("currencyCode", models.CharField(max_length=3)),
            ],
        ),
        migrations.RemoveField(
            model_name="card",
            name="accountCurrencyId",
        ),
        migrations.AddField(
            model_name="card",
            name="accountCurrency",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="cardAccountCurrency",
                to="debit_api.currency",
            ),
            preserve_default=False,
        ),
    ]
