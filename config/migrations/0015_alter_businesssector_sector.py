# Generated by Django 4.1 on 2024-07-25 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0014_claimantdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businesssector',
            name='sector',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
