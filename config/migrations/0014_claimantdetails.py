# Generated by Django 4.1 on 2024-07-12 08:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0013_alter_agent_entity_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClaimantDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('surname', models.CharField(max_length=60)),
                ('id_number', models.CharField(max_length=60)),
                ('id_type', models.CharField(max_length=60)),
                ('email', models.CharField(max_length=60)),
                ('phone_number', models.CharField(max_length=60)),
                ('bank', models.CharField(max_length=60)),
                ('branch', models.CharField(max_length=60)),
                ('branch_code', models.CharField(max_length=60)),
                ('account_name', models.CharField(max_length=60)),
                ('account_number', models.CharField(max_length=60)),
                ('account_type', models.CharField(max_length=60)),
                ('created', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Claimant Details',
                'verbose_name_plural': 'Claimant Details',
            },
        ),
    ]
