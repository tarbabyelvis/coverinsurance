# Generated by Django 4.1 on 2024-08-07 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0035_policy_premium'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='loan_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
