# Generated by Django 4.1 on 2024-11-05 06:37

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='login_attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='password_expiry_date',
            field=models.DateTimeField(default=users.models.default_expiry_date),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('ceo', 'CEO'), ('insurance_manager', 'Insurance Manager'), ('insurance_initiator', 'Insurance Initiator'), ('insurance', 'Insurance'), ('finance_officer', 'Finance Officer'), ('it_manager', 'IT Manager'), ('it_officer', 'IT Officer'), ('records_officer', 'Records Officer'), ('internal_auditor', 'Internal Auditor')], default='ceo', max_length=25),
        ),
    ]
