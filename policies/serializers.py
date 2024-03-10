from rest_framework import serializers
from django.db import transaction
from clients.models import ClientDetails
from clients.serializers import ClientDetailsSerializer
from policies.models import Policy, Beneficiary, Dependant, PolicyPaymentSchedule


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        exclude = ["policy"]


class DependantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependant
        exclude = ["policy"]


class PolicyPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyPaymentSchedule
        exclude = ["policy"]


class PolicySerializer(serializers.ModelSerializer):
    beneficiaries = BeneficiarySerializer(many=True, required=False)
    dependants = DependantSerializer(many=True, required=False)

    class Meta:
        model = Policy
        exclude = ["deleted"]

    @transaction.atomic
    def create(self, validated_data):
        beneficiaries_data = validated_data.pop("beneficiaries", [])
        dependants_data = validated_data.pop("dependants", [])

        policy = Policy.objects.create(**validated_data)

        for beneficiary_data in beneficiaries_data:
            Beneficiary.objects.create(policy=policy, **beneficiary_data)

        for dependant_data in dependants_data:
            Dependant.objects.create(policy=policy, **dependant_data)

        return policy

    @transaction.atomic
    def update(self, instance, validated_data):
        beneficiaries_data = validated_data.pop("beneficiaries", [])
        dependants_data = validated_data.pop("dependants", [])

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


class ClientPolicyRequestSerializer(serializers.Serializer):
    client = ClientDetailsSerializer()
    policy = PolicySerializer()

    def create(self, validated_data):
        # Extract client and policy data
        client_data = validated_data.pop("client")
        policy_data = validated_data.pop("policy")

        # Create client and policy instances
        client_instance = ClientDetails.objects.create(**client_data)
        policy_instance = Policy.objects.create(**policy_data, client=client_instance)

        return {"client": client_instance, "policy": policy_instance}

    def update(self, instance, validated_data):
        # Extract client and policy data
        client_data = validated_data.pop("client")
        policy_data = validated_data.pop("policy")

        # Update client and policy instances
        client_instance = instance["client"]
        policy_instance = instance["policy"]
        for attr, value in client_data.items():
            setattr(client_instance, attr, value)
        client_instance.save()

        for attr, value in policy_data.items():
            setattr(policy_instance, attr, value)
        policy_instance.save()

        return {"client": client_instance, "policy": policy_instance}


class ClientPolicyResponseSerializer(serializers.Serializer):
    client = ClientDetailsSerializer()
    policy = PolicySerializer()
