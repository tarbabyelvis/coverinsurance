# Generated by Django 4.1 on 2024-03-07 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0006_claimtype_policy'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganisationConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Organisation Config',
                'verbose_name_plural': 'Organisation Configs',
            },
        ),
    ]
