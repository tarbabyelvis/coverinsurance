# Generated by Django 4.1 on 2024-07-31 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0033_alter_policy_entity_alter_policy_is_legacy'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='closed_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
