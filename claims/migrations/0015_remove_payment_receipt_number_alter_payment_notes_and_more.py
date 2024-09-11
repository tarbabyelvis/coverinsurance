# Generated by Django 4.1 on 2024-09-09 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0014_remove_payment_payment_type_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='receipt_number',
        ),
        migrations.AlterField(
            model_name='payment',
            name='notes',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
