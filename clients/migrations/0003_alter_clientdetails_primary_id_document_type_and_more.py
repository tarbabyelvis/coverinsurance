# Generated by Django 4.1 on 2024-03-03 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_iddocumenttype_alter_claimfields_options_and_more'),
        ('clients', '0002_clientdetails_upload_ref_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientdetails',
            name='primary_id_document_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='id_document_type', to='config.iddocumenttype'),
        ),
        migrations.DeleteModel(
            name='IdDocumentType',
        ),
    ]
