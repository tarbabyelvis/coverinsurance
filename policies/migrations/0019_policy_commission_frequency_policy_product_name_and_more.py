# Generated by Django 4.1 on 2024-03-24 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0018_alter_policy_sum_insured'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='commission_frequency',
            field=models.CharField(blank=True, choices=[('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), ('Annual', 'Annual'), ('Semi Annual', 'Semi Annual'), ('Bi Annual', 'Bi Annual'), ('Once Off', 'Once Off')], default='Monthly', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='policy',
            name='product_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='policy',
            name='sub_scheme',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='policy',
            name='premium_frequency',
            field=models.CharField(blank=True, choices=[('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), ('Annual', 'Annual'), ('Semi Annual', 'Semi Annual'), ('Bi Annual', 'Bi Annual'), ('Once Off', 'Once Off')], default='Monthly', max_length=50, null=True),
        ),
    ]
