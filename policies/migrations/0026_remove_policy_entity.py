# Generated by Django 4.1 on 2024-07-25 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0025_alter_premiumpayment_branch_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='entity',
        ),
    ]
