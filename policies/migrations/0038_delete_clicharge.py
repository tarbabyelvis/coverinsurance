# Generated by Django 4.1 on 2024-09-04 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0037_policy_is_warned_of_non_payment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CliCharge',
        ),
    ]
