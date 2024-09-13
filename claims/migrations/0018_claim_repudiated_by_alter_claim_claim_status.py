# Generated by Django 4.1 on 2024-09-13 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0017_claimdocument_actual_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='repudiated_by',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='claim',
            name='claim_status',
            field=models.CharField(choices=[('CREATED', 'Created'), ('ON_ASSESSMENT', 'On Assessment'), ('SUBMITTED', 'Submitted'), ('REVIEW', 'Review'), ('APPROVED', 'Approved'), ('PAID', 'Paid'), ('REPUDIATED', 'Repudiated')], default='CREATED', max_length=30),
        ),
    ]
