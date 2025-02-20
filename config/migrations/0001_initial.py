# Generated by Django 4.1 on 2024-02-19 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClaimType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(max_length=200)),
                ('category', models.CharField(choices=[('CLIENT_DOCUMENT', 'Client Document'), ('POLICY_DOCUMENT', 'Policy Document'), ('CLAIM_DOCUMENT', 'Claim Document')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='InsuranceCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Insurance Company',
                'verbose_name_plural': 'Insurance Companies',
            },
        ),
        migrations.CreateModel(
            name='PolicyName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('policy_type', models.CharField(choices=[('FUNERAL_COVER', 'Funeral Cover'), ('CREDIT_LIFE', 'Credit Life')], max_length=20)),
            ],
            options={
                'verbose_name': 'Policy Name',
                'verbose_name_plural': 'Policy Names',
            },
        ),
        migrations.CreateModel(
            name='Relationships',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ClaimFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('input_type', models.CharField(max_length=200)),
                ('is_required', models.BooleanField(default=False)),
                ('claim_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='claims_fields', to='config.claimtype')),
            ],
        ),
    ]
