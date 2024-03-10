# Generated by Django 4.1 on 2024-03-08 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0008_policytypefields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policytypefields',
            options={'verbose_name': 'Policy Type Field', 'verbose_name_plural': 'Policy Type Fields'},
        ),
        migrations.AddField(
            model_name='claimfields',
            name='is_unique',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='policytypefields',
            name='is_unique',
            field=models.BooleanField(default=False),
        ),
    ]
