# Generated by Django 4.1 on 2024-03-17 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0017_alter_policy_business_unit_alter_policy_sum_insured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='sum_insured',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
    ]
