# Generated by Django 4.1 on 2024-03-24 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0013_alter_clientemploymentdetails_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientdetails',
            name='client_details',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientdetails',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='clientdetails',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
