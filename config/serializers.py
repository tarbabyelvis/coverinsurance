from rest_framework import serializers
from .models import *


class PolicyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyName
        fields = [
            "id",
            "name",
            "policy_type",
            "default_commission",
            "has_beneficiaries",
            "has_dependencies",
        ]


class InsuranceCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = ["id", "name"]


class ClaimTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimType
        fields = ["id", "name"]


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ["id", "document_type", "category"]


class RelationshipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationships
        fields = "id", ["name"]


class IdDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdDocumentType
        fields = ["id", "type_name"]


class BusinessSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSector
        fields = ["id", "sector"]


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ["id", "agent_name", "entity_type", "phone_number", "email"]


class ClaimFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimFields
        fields = ["short_name", "name", "input_type", "is_required", "is_unique"]


class PolicyTypeFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyTypeFields
        fields = ["short_name", "name", "input_type", "is_required", "is_unique"]
