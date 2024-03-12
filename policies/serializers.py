from django.forms import model_to_dict
from rest_framework import serializers
from django.db import transaction
from clients.models import ClientDetails
from clients.serializers import ClientDetailsSerializer
from core.utils import convert_to_datetime
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
        # You can make client field required or not based on context
        extra_kwargs = {"client": {"required": True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if 'request' is in the context
        if not "request" in self.context:
            # If 'request' does not exists, it means this serializer is nested in ClientPolicyRequestSerializer
            # In that case, client field is not required
            self.fields["client"].required = False

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

    def to_internal_value(self, data):
        # Convert QueryDict to a mutable dictionary
        mutable_data = data.copy()

        # Convert datetime to date for specified fields if needed
        for field in ["commencement_date", "expiry_date"]:
            if field in mutable_data["policy"] and isinstance(
                mutable_data["policy"][field], str
            ):
                date_time = convert_to_datetime(mutable_data["policy"][field])
                if date_time is not None:
                    mutable_data["policy"][field] = date_time.date()
        if "policy_status" in mutable_data["policy"] and (
            isinstance(mutable_data["policy"]["policy_status"], int)
            or str(mutable_data["policy"]["policy_status"]).isdigit()
        ):
            print(mutable_data["policy"]["policy_status"])
            status_mapping = {"1": "A"}
            mutable_data["policy"]["policy_status"] = status_mapping.get(
                mutable_data["policy"]["policy_status"], "X"
            )
            print(mutable_data["policy"]["policy_status"])

        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        # Extract client and policy data
        client_data = validated_data.pop("client")
        policy_data = validated_data.pop("policy")

        # Create client and policy instances
        client_instance = ClientDetails.objects.create(**client_data)

        policy_data.pop("client")  # Remove client from policy data
        policy_instance = Policy.objects.create(client=client_instance, **policy_data)

        return {
            "client": model_to_dict(client_instance),
            "policy": model_to_dict(policy_instance),
        }

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
