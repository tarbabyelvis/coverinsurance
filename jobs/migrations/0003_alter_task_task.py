# Generated by Django 4.1 on 2024-06-06 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_tasklog_data_tasklog_manual_run_alter_task_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task',
            field=models.CharField(choices=[('LIFE_FUNERAL_DAILY', 'life_funeral'), ('CREDIT_LIFE_DAILY', 'credit_life'), ('LIFE_CLAIMS_DAILY', 'life_claims')], max_length=30),
        ),
    ]
