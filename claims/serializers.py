from datetime import datetime

from rest_framework import serializers

from config.models import ClaimType, DocumentType, IdDocumentType
from core.enums import ClaimStatus
from policies.models import Policy
from policies.serializers import PolicySerializer
from .models import Claim, ClaimDocument


class ClaimTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimType
        ref_name = "ClaimsClaimTypeSerializer"
        fields = ["id", "name"]  # Assuming you want to serialize only 'id' and 'name'


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ["id", "name"]  # Assuming you want to serialize only 'id' and 'name'


class ClaimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDocument
        fields = ["id", "claim", "document_name", "document_file", "document_type"]


class ClaimSerializer(serializers.ModelSerializer):
    claim_type = serializers.PrimaryKeyRelatedField(queryset=ClaimType.objects.all())
    claim_document = ClaimDocumentSerializer(many=True, required=False)
    policy = serializers.PrimaryKeyRelatedField(queryset=Policy.objects.all())

    class Meta:
        model = Claim
        fields = "__all__"

    def validate_rejected_date(self, value):
        if value:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                raise serializers.ValidationError(
                    "Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
        return value

    def to_internal_value(self, data):
        if "claimant_id_type" in data:
            claimant_id_type = data["claimant_id_type"]
            if isinstance(claimant_id_type, str):
                # Try to convert string to integer if it's a digit
                if claimant_id_type.isdigit():
                    data["claimant_id_type"] = int(claimant_id_type)
                else:
                    try:
                        data["claimant_id_type"] = IdDocumentType.objects.get(
                            name=claimant_id_type
                        ).id
                    except IdDocumentType.DoesNotExist:
                        raise serializers.ValidationError(
                            "Invalid claimant id type name"
                        )
            elif not isinstance(claimant_id_type, int):
                raise serializers.ValidationError(
                    "claimant_id_type must be an integer or string"
                )
        if 'rejected_date' in data and not data['rejected_date']:
            data['rejected_date'] = None
        if 'claim_assessment_date' in data and not data['claim_assessment_date']:
            data['claim_assessment_date'] = None
        if 'claim_paid_date' in data and not data['claim_paid_date']:
            data['claim_paid_date'] = None
        if 'repudiated_date' in data and not data['repudiated_date']:
            data['repudiated_date'] = None
        if "claim_status" in data:
            if "claim_status" in data:
                claim_status = data["claim_status"]
                if isinstance(claim_status, str):
                    valid_status = next(
                        (key for key, label in ClaimStatus.choices if label == claim_status),
                        None
                    )
                    if valid_status:
                        data["claim_status"] = valid_status
                else:
                    raise serializers.ValidationError(
                        {"claim_status": "Invalid claim status"})

        return super().to_internal_value(data)

    def create(self, validated_data):
        claim_documents_data = validated_data.pop("claim_document", [])
        claim = Claim.objects.create(**validated_data)
        for claim_document_data in claim_documents_data:
            ClaimDocument.objects.create(claim=claim, **claim_document_data)
        return claim

    def update(self, instance, validated_data):
        claim_documents_data = validated_data.pop("claim_document", [])
        claim_documents = instance.claim_document.all()
        claim_documents = list(claim_documents)
        instance = super().update(instance, validated_data)
        for claim_document_data in claim_documents_data:
            claim_document = claim_documents.pop(0)
            claim_document.document_name = claim_document_data.get(
                "document_name", claim_document.document_name
            )
            claim_document.document_file = claim_document_data.get(
                "document_file", claim_document.document_file
            )
            claim_document.document_type = claim_document_data.get(
                "document_type", claim_document.document_type
            )
            claim_document.save()
        return instance
