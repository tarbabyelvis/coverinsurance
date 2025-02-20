# Generated by Django 4.1 on 2024-03-17 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0015_policypaymentschedule_term'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='business_unit',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='policy',
            name='premium_frequency',
            field=models.CharField(blank=True, choices=[('Monthly', 'Monthly'), ('Once Off', 'Once Off')], default='Monthly', max_length=50, null=True),
        ),
    ]
