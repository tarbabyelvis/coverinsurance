from rest_framework import serializers
from .models import *


class PolicyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyName
        fields = ["name", "policy_type"]

class InsuranceCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = ["name"]

class ClaimTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimType
        fields = ["name"]

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ["document_type", "category"]

class RelationshipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationships
        fields = ["name"]

class IdDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdDocumentType
        fields = ["type_name"]

class BusinessSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSector
        fields = ["sector"]

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ["agent_name", "entity_type", "phone_number", "email"]


class ClaimFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimFields
        fields = ["short_name", "name", "input_type", "is_required", "is_unique"]


class PolicyTypeFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyTypeFields
        fields = ["short_name", "name", "input_type", "is_required", "is_unique"]

