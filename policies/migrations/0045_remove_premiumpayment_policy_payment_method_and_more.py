# Generated by Django 4.1 on 2024-10-23 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0044_remove_premiumpayment_client_transaction_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='premiumpayment',
            name='policy_payment_method',
        ),
        migrations.RemoveField(
            model_name='premiumpayment',
            name='transaction_type',
        ),
        migrations.AlterField(
            model_name='policy',
            name='policy_status',
            field=models.CharField(choices=[('A', 'Active'), ('L', 'Lapsed'), ('X', 'Cancelled'), ('E', 'Expiry'), ('C', 'Claimed'), ('R', 'Reinstated'), ('N', 'Not Taken Up (Non payment of premium)'), ('P', 'Paid Up'), ('F', 'Paid Up'), ('S', 'Surrendered'), ('SR', 'Surrendered due to replacement'), ('T', 'Transferred out'), ('HL', 'Historic Lapsed')], max_length=20),
        ),
        migrations.AlterField(
            model_name='statussnapshot',
            name='policy_status',
            field=models.CharField(choices=[('A', 'Active'), ('L', 'Lapsed'), ('X', 'Cancelled'), ('E', 'Expiry'), ('C', 'Claimed'), ('R', 'Reinstated'), ('N', 'Not Taken Up (Non payment of premium)'), ('P', 'Paid Up'), ('F', 'Paid Up'), ('S', 'Surrendered'), ('SR', 'Surrendered due to replacement'), ('T', 'Transferred out'), ('HL', 'Historic Lapsed')], max_length=20),
        ),
        migrations.AddConstraint(
            model_name='beneficiary',
            constraint=models.UniqueConstraint(condition=models.Q(('primary_id_number', ''), _negated=True), fields=('primary_id_number',), name='unique_beneficiary_primary_id_number_when_set'),
        ),
        migrations.AddConstraint(
            model_name='dependant',
            constraint=models.UniqueConstraint(condition=models.Q(('primary_id_number', ''), _negated=True), fields=('primary_id_number',), name='unique_dependant_primary_id_number_when_set'),
        ),
    ]
