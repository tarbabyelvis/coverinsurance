# Generated by Django 4.1 on 2024-03-15 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0002_alter_claim_claimant_id_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='claim',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterModelOptions(
            name='claimdocument',
            options={'ordering': ['-pk']},
        ),
    ]
