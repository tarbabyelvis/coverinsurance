from rest_framework import serializers
from .models import Claim, ClaimDocument
from config.models import ClaimType, DocumentType

class ClaimTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimType
        fields = ['id', 'name']  # Assuming you want to serialize only 'id' and 'name'

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name']  # Assuming you want to serialize only 'id' and 'name'

class ClaimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDocument
        fields = ['id', 'claim', 'document_name', 'document_file', 'document_type']

class ClaimSerializer(serializers.ModelSerializer):
    claim_type = serializers.PrimaryKeyRelatedField(queryset=ClaimType.objects.all())
    claim_document = ClaimDocumentSerializer(many=True, required=False)

    class Meta:
        model = Claim
        fields = '__all__'

    def create(self, validated_data):
        claim_documents_data = validated_data.pop('claim_document', [])
        claim = Claim.objects.create(**validated_data)
        for claim_document_data in claim_documents_data:
            ClaimDocument.objects.create(claim=claim, **claim_document_data)
        return claim

    def update(self, instance, validated_data):
        claim_documents_data = validated_data.pop('claim_document', [])
        claim_documents = instance.claim_document.all()
        claim_documents = list(claim_documents)
        instance = super().update(instance, validated_data)
        for claim_document_data in claim_documents_data:
            claim_document = claim_documents.pop(0)
            claim_document.document_name = claim_document_data.get('document_name', claim_document.document_name)
            claim_document.document_file = claim_document_data.get('document_file', claim_document.document_file)
            claim_document.document_type = claim_document_data.get('document_type', claim_document.document_type)
            claim_document.save()
        return instance
