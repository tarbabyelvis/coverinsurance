from django.forms import model_to_dict
from rest_framework import serializers
from django.db import IntegrityError, transaction
from clients.models import ClientDetails, ClientEmploymentDetails
from clients.serializers import ClientDetailsSerializer
from config.models import BusinessSector, Relationships
from config.serializers import AgentSerializer, InsuranceCompanySerializer
from core.utils import convert_to_datetime
from policies.constants import STATUS_MAPPING
from policies.models import Policy, Beneficiary, Dependant, PolicyPaymentSchedule
from datetime import datetime
from rest_framework.fields import empty


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        exclude = ["policy", "deleted"]

    def validate_policy(self, value):
        # Validate if the policy exists
        if not Policy.objects.filter(id=value).exists():
            raise serializers.ValidationError("Policy does not exist.")
        return value

    def create(self, validated_data):
        # Extract policy and relationship from validated data
        policy_id = validated_data.pop("policy")
        relationship_id = validated_data.pop("relationship")

        # Get the policy and relationship instances
        policy = Policy.objects.get(id=policy_id)
        relationship = Relationships.objects.get(id=relationship_id)

        # Create and return the dependant instance
        beneficiary = Beneficiary.objects.create(
            policy=policy, relationship=relationship.pk, **validated_data
        )
        return beneficiary


class DependantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dependant
        exclude = ["policy", "deleted"]

    # def validate_policy(self, value):
    #     # Validate if the policy exists
    #     if not Policy.objects.filter(id=value).exists():
    #         raise serializers.ValidationError("Policy does not exist.")
    #     return value

    def create(self, validated_data):
        # Extract policy and relationship from validated data
        policy_id = validated_data.pop("policy")
        relationship_id = validated_data.pop("relationship")

        # Get the policy and relationship instances
        policy = Policy.objects.get(id=policy_id)
        relationship = Relationships.objects.get(id=relationship_id)

        # Create and return the dependant instance
        dependant = Dependant.objects.create(
            policy=policy, relationship=relationship.pk, **validated_data
        )
        return dependant


class PolicyPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyPaymentSchedule
        exclude = ["policy"]


class PolicySerializer(serializers.ModelSerializer):
    # beneficiaries = BeneficiarySerializer(many=True, required=False)
    # dependants = DependantSerializer(many=True, required=False)
    client = ClientDetailsSerializer(read_only=True)
    insurer = InsuranceCompanySerializer(read_only=True)
    agent = AgentSerializer(read_only=True)

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
    client = ClientDetailsSerializer(read_only=True)
    insurer = InsuranceCompanySerializer(read_only=True)
    agent = AgentSerializer(read_only=True)
    policy_beneficiary = BeneficiarySerializer(many=True)
    policy_dependants = DependantSerializer(many=True)
    # Add other nested serializers for related models here

    # class Meta(PolicySerializer.Meta):
    #     fields = '__all__'


class ClientPolicyRequestSerializer(serializers.Serializer):
    client = ClientDetailsSerializer()
    policy = PolicySerializer()

    def to_internal_value(self, data):
        # Deep copy the data to avoid modifying the original object
        mutable_data = data.copy()

        # Convert datetime to date for specified fields if needed
        for field in ["commencement_date", "expiry_date"]:
            if field in mutable_data.get("policy", {}) and isinstance(
                mutable_data["policy"][field], str
            ):
                date_time = convert_to_datetime(mutable_data["policy"][field])
                if date_time is not None:
                    mutable_data["policy"][field] = date_time.date()
            if field in mutable_data.get("policy", {}) and isinstance(
                mutable_data["policy"][field], datetime
            ):
                mutable_data["policy"][field] = mutable_data[field].date()

        # Convert policy_status to a proper format if needed
        if "policy_status" in mutable_data.get("policy", {}):
            policy_status = mutable_data["policy"]["policy_status"]
            if isinstance(policy_status, int) or str(policy_status).isdigit():
                status_mapping = {"1": "A"}
                mutable_data["policy"]["policy_status"] = status_mapping.get(
                    str(policy_status), "X"
                )
            else:
                mutable_data["policy"]["policy_status"] = STATUS_MAPPING.get(
                    str(policy_status), mutable_data["policy"]["policy_status"]
                )

        # Convert datetime to date for the 'date_of_birth' field if needed
        client_data = mutable_data.get("client", {})
        if "date_of_birth" in client_data:
            date_of_birth = client_data["date_of_birth"]
            if isinstance(date_of_birth, datetime):
                client_data["date_of_birth"] = date_of_birth.strftime("%Y-%m-%d")
            elif isinstance(date_of_birth, str):
                client_data["date_of_birth"] = convert_to_datetime(date_of_birth)

        return super().to_internal_value(mutable_data)

    @transaction.atomic
    def create(self, validated_data):
        print("trying to save")
        client_data = validated_data.pop("client")
        policy_data = validated_data.pop("policy")
        print(policy_data)
        beneficiaries_data = (
            policy_data.pop("beneficiaries") if "beneficiaries" in policy_data else []
        )
        dependants_data = (
            policy_data.pop("dependants") if "dependants" in policy_data else []
        )
        employment_details_data = (
            client_data.pop("employment_details")
            if "employment_details" in client_data
            else None
        )

        # Check if the client with the primary ID number already exists
        client_instance, _ = ClientDetails.objects.get_or_create(
            primary_id_number=client_data["primary_id_number"],
            defaults=client_data,
        )

        # Create or update ClientEmploymentDetails
        if employment_details_data:
            if str(employment_details_data["sector"]).isdigit():
                try:
                    employment_details_data["sector"] = BusinessSector.objects.get(
                        pk=employment_details_data["sector"]
                    )
                except BusinessSector.DoesNotExist:
                    raise serializers.ValidationError("Business sector does not exist.")
            ClientEmploymentDetails.objects.update_or_create(
                client=client_instance, defaults=employment_details_data
            )

        # Check if the policy with the policy number and external reference already exists
        try:
            if "policy_number" in policy_data and policy_data["policy_number"]:
                policy_instance, _ = Policy.objects.get_or_create(
                    policy_number=policy_data["policy_number"],
                    defaults={"client": client_instance, **policy_data},
                )
            else:
                print("Here we go again")
                print(policy_data)
                policy_instance = Policy.objects.create(
                    client=client_instance, **policy_data
                )
        except IntegrityError:
            # Handle the case where the policy number or external reference already exists
            # You can raise appropriate validation error or handle it as per your requirement
            raise serializers.ValidationError(
                "Policy with the given policy number or external reference already exists."
            )

        # Create beneficiaries and dependants
        for beneficiary_data in beneficiaries_data:
            Beneficiary.objects.create(policy=policy_instance, **beneficiary_data)

        for dependant_data in dependants_data:
            Dependant.objects.create(policy=policy_instance, **dependant_data)

        return {
            "client": ClientDetailsSerializer(client_instance).data,
            "policy": PolicySerializer(policy_instance).data,
        }

    @transaction.atomic
    def update(self, instance, validated_data):
        client_data = validated_data.pop("client", None)
        policy_data = validated_data.pop("policy", None)

        if client_data:
            # Update client instance
            ClientDetails.objects.update_or_create(
                defaults=client_data, **instance.client
            )

        if policy_data:
            # Update policy instance
            Policy.objects.update_or_create(
                defaults=policy_data, client=instance.client
            )

        return instance

    # def run_validation(self, data=empty):
    #     """
    #     Bypass uniqueness checks when running validation.
    #     """
    #     try:
    #         # Temporarily remove the unique validation check
    #         client_serializer = ClientDetailsSerializer()
    #         policy_serializer = PolicySerializer()
    #         client_serializer.validators = [
    #             v
    #             for v in client_serializer.validators
    #             if "UniqueValidator" not in str(v)
    #         ]
    #         policy_serializer.validators = [
    #             v
    #             for v in policy_serializer.validators
    #             if "UniqueValidator" not in str(v)
    #         ]
    #         self.fields["client"] = client_serializer
    #         self.fields["policy"] = policy_serializer
    #         return super().run_validation(data)
    #     finally:
    #         # Restore the original validators
    #         self.fields["client"] = ClientDetailsSerializer()
    #         self.fields["policy"] = PolicySerializer()


class ClientPolicyResponseSerializer(serializers.Serializer):
    client = ClientDetailsSerializer()
    policy = PolicySerializer()
