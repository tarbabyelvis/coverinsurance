# Generated by Django 4.1 on 2024-03-05 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0004_agent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iddocumenttype',
            name='created',
        ),
        migrations.RemoveField(
            model_name='iddocumenttype',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='iddocumenttype',
            name='updated',
        ),
    ]
