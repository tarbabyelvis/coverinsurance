# Generated by Django 4.1 on 2024-09-23 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0038_delete_clicharge'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoverCharges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('policy_type', models.CharField(choices=[('FUNERAL_COVER', 'Funeral Cover'), ('CREDIT_LIFE', 'Credit Life')], max_length=20)),
                ('package', models.CharField(max_length=50, null=True)),
                ('benefit_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('premium', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'ordering': ['-pk'],
                'abstract': False,
            },
        ),
    ]
