# Generated by Django 4.1 on 2024-03-15 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0008_alter_policy_external_reference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiary',
            name='beneficiary_gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')], max_length=20),
        ),
        migrations.AlterField(
            model_name='dependant',
            name='dependant_gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')], max_length=20),
        ),
    ]
