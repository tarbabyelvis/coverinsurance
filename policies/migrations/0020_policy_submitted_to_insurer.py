# Generated by Django 4.1 on 2024-03-24 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0019_policy_commission_frequency_policy_product_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='submitted_to_insurer',
            field=models.BooleanField(default=False),
        ),
    ]
