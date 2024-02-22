# Generated by Django 4.1 on 2024-02-19 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClientDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=200)),
                ('middle_name', models.CharField(blank=True, max_length=200, null=True)),
                ('last_name', models.CharField(blank=True, max_length=200, null=True)),
                ('primary_id_number', models.CharField(max_length=200)),
                ('external_id', models.CharField(blank=True, max_length=200, null=True)),
                ('entity_type', models.CharField(choices=[('PERSON', 'Person'), ('ORGANIZATION', 'Organization')], max_length=20)),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=20)),
                ('marital_status', models.CharField(blank=True, choices=[('MARRIED', 'Married'), ('SINGLE', 'Single'), ('DIVORCED', 'Divorced'), ('WIDOWED', 'Widowed'), ('OTHER', 'Other'), ('UNKNOWN', 'Unknown')], max_length=20, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=200, null=True)),
                ('address_street', models.CharField(blank=True, max_length=200, null=True)),
                ('address_suburb', models.CharField(blank=True, max_length=200, null=True)),
                ('address_town', models.CharField(blank=True, max_length=200, null=True)),
                ('address_province', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Client Details',
                'verbose_name_plural': 'Client Details',
            },
        ),
        migrations.CreateModel(
            name='IdDocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('type_name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Loan Team',
                'verbose_name_plural': 'Loan Teams',
            },
        ),
        migrations.CreateModel(
            name='ClientEmploymentDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('employer_name', models.CharField(max_length=200)),
                ('employer_address_street', models.CharField(blank=True, max_length=200, null=True)),
                ('employer_address_suburb', models.CharField(blank=True, max_length=200, null=True)),
                ('employer_address_town', models.CharField(blank=True, max_length=200, null=True)),
                ('employer_address_province', models.CharField(blank=True, max_length=200, null=True)),
                ('employer_phone_number', models.CharField(blank=True, max_length=200, null=True)),
                ('employer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('employer_website', models.CharField(blank=True, max_length=200, null=True)),
                ('gross_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('basic_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('job_title', models.CharField(blank=True, max_length=200, null=True)),
                ('sector', models.CharField(blank=True, max_length=200, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_employment_details', to='clients.clientdetails')),
            ],
            options={
                'verbose_name': 'Client Details',
                'verbose_name_plural': 'Client Details',
            },
        ),
        migrations.AddField(
            model_name='clientdetails',
            name='primary_id_document_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='id_document_type', to='clients.iddocumenttype'),
        ),
    ]
