# Generated by Django 4.1 on 2024-06-25 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0004_claim_policy'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='rejected_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='claim',
            name='rejected_reason',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
