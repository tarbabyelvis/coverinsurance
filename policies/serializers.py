from decimal import Decimal
from rest_framework import serializers
from django.db import IntegrityError, transaction
from clients.models import ClientDetails, ClientEmploymentDetails
from clients.serializers import ClientDetailsSerializer
from config.models import BusinessSector, InsuranceCompany, Relationships
from config.serializers import AgentSerializer, InsuranceCompanySerializer
from core.utils import convert_to_datetime
from policies.constants import STATUS_MAPPING
from policies.models import (
    Policy,
    Beneficiary,
    Dependant,
    PolicyPaymentSchedule,
    PremiumPayment,
    PremiumPaymentScheduleLink,
)
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.validators import UniqueValidator


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
        if isinstance(relationship_id, Relationships):
            relationship = relationship_id
        else:
            relationship = Relationships.objects.get(id=relationship_id)

        # Create and return the dependant instance
        beneficiary = Beneficiary.objects.create(
            policy=policy, relationship=relationship, **validated_data
        )
        return beneficiary


class DependantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dependant
        exclude = ["policy", "deleted"]

    def create(self, validated_data):
        # Extract policy and relationship from validated data
        policy_id = validated_data.pop("policy")
        relationship_id = validated_data.pop("relationship")

        # Get the policy and relationship instances
        policy = Policy.objects.get(id=policy_id)
        if isinstance(relationship_id, Relationships):
            relationship = relationship_id
        else:
            relationship = Relationships.objects.get(id=relationship_id)

        # Create and return the dependant instance
        dependant = Dependant.objects.create(
            policy=policy, relationship=relationship, **validated_data
        )
        return dependant


class PolicyPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyPaymentSchedule
        exclude = ["policy"]


class PolicySerializer(serializers.ModelSerializer):

    def validate_policy_number(self, value):
        print("Validating policy number")
        return value

    def validate(self, data):
        print("validating policy")
        errors = {}

        # Define fields that should not be None
        non_nullable_fields = [
            "policy_type",
            "client",
            "sum_insured",
            "insurer",
            "policy_status",
        ]

        # Remove the UniqueValidator for policy_number if it exists
        unique_validators = [
            validator
            for validator in self.fields.get("policy_number").validators
            if isinstance(validator, UniqueValidator)
        ]
        for validator in unique_validators:
            self.fields["policy_number"].validators.remove(validator)

        # Iterate over each field in the serializer
        for field_name, value in data.items():
            # Get the corresponding model field
            model_field = self.fields[field_name]

            # Check if the field is supposed to be non-nullable
            if field_name in non_nullable_fields and value is None:
                errors[field_name] = ["This field cannot be None."]
                continue

            # Validate the data type
            try:
                if value is not None:
                    data[field_name] = model_field.to_internal_value(value)

            except serializers.ValidationError as e:
                print(f"Error with datatypes for {field_name} {value}")
                errors[field_name] = e.detail
            except DjangoValidationError as e:
                errors[field_name] = f"Invalid email address {value}"
            except Exception as e:
                print("Error: ", e)

        if errors:
            print("Error validation")
            raise serializers.ValidationError(errors)
        print("Done validation policy data")
        return data

    def to_internal_value(self, data):
        # Convert QueryDict to a mutable dictionary
        mutable_data = data.copy()

        if "client" in mutable_data and isinstance(
            mutable_data["client"], ClientDetails
        ):
            # If the value is an instance of ClientDetails, use it directly
            mutable_data["client"] = mutable_data["client"].pk
        elif "client" in mutable_data and isinstance(mutable_data["client"], str):
            # If the value is a string, check if it's a number
            if mutable_data["client"].isdigit():
                # If it's a number, retrieve the ClientDetails instance using the primary key
                mutable_data["client"] = ClientDetails.objects.get(
                    pk=mutable_data["client"]
                ).pk
            else:
                raise serializers.ValidationError("Invalid client ID.")

        elif "client" in mutable_data:
            # If it's already a primary key, retrieve the ClientDetails instance using the primary key
            try:
                mutable_data["client"] = ClientDetails.objects.get(
                    pk=mutable_data["client"]
                ).pk
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Invalid client ID.")

        # Convert policy_status to a proper format if needed
        if "policy_status" in mutable_data:
            policy_status = mutable_data["policy_status"]
            if isinstance(policy_status, int) or str(policy_status).isdigit():
                status_mapping = {"1": "A"}
                mutable_data["policy_status"] = status_mapping.get(
                    str(policy_status), "X"
                )
            else:
                mutable_data["policy_status"] = STATUS_MAPPING.get(
                    str(policy_status), mutable_data["policy_status"]
                )

        ## Handle rounding and casting for decimal fields
        for field_name in [
            "sum_insured",
            "total_premium",
            "commission_amount",
            "admin_fee",
        ]:
            if field_name in mutable_data:
                try:
                    mutable_data[field_name] = float(mutable_data[field_name])
                    mutable_data[field_name] = round(mutable_data[field_name], 2)
                except (ValueError, TypeError):
                    mutable_data[field_name] = 0

        return super().to_internal_value(mutable_data)

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
        print("create policy")
        beneficiaries_data = validated_data.pop("beneficiaries", [])
        dependants_data = validated_data.pop("dependants", [])
        terms = validated_data.get("policy_term", 1)  # Default to 1 if not provided

        # Calculate payment due date
        payment_due_date = validated_data["commencement_date"] + timedelta(days=30)

        # Calculate amount due per term
        amount_due_per_term = validated_data["total_premium"] / terms

        # Create the policy instance
        policy = Policy.objects.create(**validated_data)

        # Create payment schedules for each term
        print("before creating schedule")
        for term in range(1, terms + 1):
            print("creating the schedule")
            payment_schedule = PolicyPaymentSchedule.objects.create(
                term=term,
                policy=policy,
                payment_date=payment_due_date,
                payment_due_date=payment_due_date,
                amount_due=amount_due_per_term,
            )

            # Increment payment due date by one month
            payment_due_date += timedelta(days=30)

        # Create beneficiaries and dependants
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


class PolicyListSerializer(serializers.ModelSerializer):
    client = ClientDetailsSerializer(read_only=True)
    insurer = InsuranceCompanySerializer(read_only=True)
    agent = AgentSerializer(read_only=True)
    policy_beneficiary = BeneficiarySerializer(read_only=True)
    policy_dependants = DependantSerializer(read_only=True)

    class Meta:
        model = Policy
        exclude = ["deleted"]


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
                print("it is a date instance")
                mutable_data["policy"][field] = mutable_data["policy"][field].date()

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

        # Convert insurer to proper datatype
        print("completed the policy check")
        return super().to_internal_value(mutable_data)

    @transaction.atomic
    def create(self, validated_data):
        print("saving transaction")
        client_data = validated_data.pop("client")
        policy_data = validated_data.pop("policy")
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

        insurer = policy_data["insurer"]

        if isinstance(insurer, int) or str(insurer).isdigit():
            insurance_company = InsuranceCompany.objects.get(pk=insurer)
            policy_data["insurer"] = insurance_company

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
            print("trying to create a policy")
            if "policy_number" in policy_data and policy_data["policy_number"]:
                policy_instance, created = Policy.objects.get_or_create(
                    policy_number=policy_data["policy_number"],
                    defaults={"client": client_instance, **policy_data},
                )

                if created:
                    terms = validated_data.get("policy_term", 1)
                    amount_due_per_term = validated_data["total_premium"] / terms
                    # create payment schedule
                    for term in range(1, terms + 1):
                        PolicyPaymentSchedule.objects.create(
                            term=term,
                            policy=policy_instance,
                            payment_date=payment_due_date,
                            payment_due_date=payment_due_date,
                            amount_due=amount_due_per_term,
                        )

                        # Increment payment due date by one month
                        payment_due_date += timedelta(days=30)

            else:
                policy_instance = Policy.objects.create(
                    client=client_instance, **policy_data
                )
        except IntegrityError as e:
            print(e)
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


class ClientPolicyResponseSerializer(serializers.Serializer):
    client = ClientDetailsSerializer()
    policy = PolicySerializer()


class PremiumPaymentSerializer(serializers.ModelSerializer):
    payment_receipt = serializers.FileField(required=False)
    payment_receipt_date = serializers.DateField(required=False)
    payment_method = serializers.CharField(max_length=200, required=False)
    payment_reference = serializers.CharField(max_length=200, required=False)

    class Meta:
        model = PremiumPayment
        exclude = ["policy"]

    def get_fields(self):
        fields = super().get_fields()
        context = self.context.get("request")

        # Exclude certain fields if the context indicates creation
        if context and context.method == "POST":
            fields.pop("deleted", None)
            fields.pop("is_reversed", None)

        return fields

    @transaction.atomic
    def create(self, validated_data):
        policy_id = validated_data.pop("policy")
        try:
            policy = Policy.objects.get(pk=policy_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Policy with the provided ID does not exist."
            )

        payment_schedules = PolicyPaymentSchedule.objects.filter(
            policy=policy
        ).order_by("-id")

        amount_paid = validated_data.get("amount")
        payment_date = validated_data.get("payment_date")

        premium_payment = PremiumPayment.objects.create(**validated_data, policy=policy)

        for schedule in payment_schedules:
            amount_due = schedule.amount_due

            # Initialize amount_paid to 0 if it's None
            if schedule.amount_paid is None:
                schedule.amount_paid = Decimal("0")

            # Calculate the amount to pay for this schedule
            amount_to_pay = min(amount_paid, amount_due)

            # Update the payment schedule
            schedule.amount_paid += amount_to_pay
            schedule.amount_due -= amount_to_pay
            schedule.payment_date = payment_date
            schedule.payment_due_date = (
                schedule.payment_due_date
            )  # Update payment_due_date as needed
            schedule.is_paid = schedule.amount_due == 0
            schedule.save()

            # Deduct the paid amount
            amount_paid -= amount_to_pay

            # Create PremiumPaymentScheduleLink
            PremiumPaymentScheduleLink.objects.create(
                premium_payment=premium_payment, policy_payment_schedule=schedule
            )

        if policy.policy_payment_schedule.filter(is_paid=False).count() == 0:
            policy.policy_status = "paid"
            policy.save()

        return premium_payment

    @transaction.atomic
    def update(self, instance, validated_data):
        # Update instance fields
        instance.amount = validated_data.get("amount", instance.amount)
        instance.payment_date = validated_data.get(
            "payment_date", instance.payment_date
        )
        instance.save()

        # Update other fields
        instance.payment_receipt = validated_data.get(
            "payment_receipt", instance.payment_receipt
        )
        instance.payment_receipt_date = validated_data.get(
            "payment_receipt_date", instance.payment_receipt_date
        )
        instance.payment_method = validated_data.get(
            "payment_method", instance.payment_method
        )
        instance.payment_reference = validated_data.get(
            "payment_reference", instance.payment_reference
        )
        instance.is_reversed = validated_data.get("is_reversed", instance.is_reversed)
        instance.deleted = validated_data.get("deleted", instance.deleted)
        instance.save()

        return instance
