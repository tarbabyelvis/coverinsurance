# Generated by Django 4.1 on 2024-03-15 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0010_alter_clientdetails_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientdetails',
            name='entity_type',
            field=models.CharField(choices=[('Individual', 'Individual'), ('Organization', 'Organization')], max_length=20),
        ),
        migrations.AlterField(
            model_name='clientdetails',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('Married', 'Married'), ('Single', 'Single'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed'), ('Other', 'Other'), ('Unknown', 'Unknown')], max_length=20, null=True),
        ),
    ]
