# Generated by Django 4.1 on 2024-09-15 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audittrail',
            name='changes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
