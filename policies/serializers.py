from rest_framework import serializers
from django.db import transaction
from policies.models import Policy, Beneficiary, Dependant, PolicyPaymentSchedule


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        exclude = ['policy']


class DependantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependant
        exclude = ['policy']

class PolicyPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyPaymentSchedule
        exclude = ['policy']


class PolicySerializer(serializers.ModelSerializer):
    beneficiaries = BeneficiarySerializer(many=True, required=False)
    dependants = DependantSerializer(many=True, required=False)

    class Meta:
        model = Policy
        exclude = ['deleted']
   
    @transaction.atomic
    def create(self, validated_data):
        beneficiaries_data = validated_data.pop('beneficiaries', [])
        dependants_data = validated_data.pop('dependants', [])
        
        policy = Policy.objects.create(**validated_data)
        
        for beneficiary_data in beneficiaries_data:
            Beneficiary.objects.create(policy=policy, **beneficiary_data)
        
        for dependant_data in dependants_data:
            Dependant.objects.create(policy=policy, **dependant_data)

        return policy

    @transaction.atomic
    def update(self, instance, validated_data):
        beneficiaries_data = validated_data.pop('beneficiaries', [])
        dependants_data = validated_data.pop('dependants', [])
        
        instance = super().update(instance, validated_data)

        # Clear existing beneficiaries and dependants
        instance.policy_beneficiary.all().delete()
        instance.policy_dependants.all().delete()

        for beneficiary_data in beneficiaries_data:
            Beneficiary.objects.create(policy=instance, **beneficiary_data)
        
        for dependant_data in dependants_data:
            Dependant.objects.create(policy=instance, **dependant_data)

        return instance


class PolicyDetailSerializer(PolicySerializer):
    policy_payment_schedule = PolicyPaymentScheduleSerializer(many=True, read_only=True)
    # Add other nested serializers for related models here

    # class Meta(PolicySerializer.Meta):
    #     fields = '__all__'