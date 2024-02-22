# serializers.py
from rest_framework import serializers
from .models import ClientDetails, IdDocumentType
from django.core.exceptions import ObjectDoesNotExist

class ClientDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDetails
        exclude = ['deleted']
        # fields = [field.name for field in ClientDetails._meta.get_fields() if field.name != 'deleted']

    def validate_primary_id_document_type(self, value):
        try:
            if isinstance(value, IdDocumentType):
                # If the value is an instance of IdDocumentType, use its primary key
                value = value.pk
            # Check if the provided ID exists in the IdDocumentType table
            IdDocumentType.objects.get(pk=value)
        except ObjectDoesNotExist:
            # If the object does not exist, raise a validation error
            raise serializers.ValidationError("Invalid primary_id_document_type ID.")
        
        return value

    def validate(self, data):
        errors = {}
        print("the data: ", data)

        # Iterate over each field in the serializer
        for field_name, value in data.items():
            # Get the corresponding model field
            model_field = self.fields[field_name]

            # Validate the data type
            try:
                # Attempt to convert the value to the correct data type
                data[field_name] = model_field.to_internal_value(value)
            except serializers.ValidationError as e:
                errors[field_name] = e.detail

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
    def create(self, validated_data):
        print("Now creating records...")
        # Extract the nested IdDocumentType data from the validated data
        primary_id_document_type_value = validated_data.pop('primary_id_document_type')
        if isinstance(primary_id_document_type_value, IdDocumentType):
            # If the value is an instance of IdDocumentType, use its primary key
            primary_id_document_type_pk = primary_id_document_type_value.pk
        else:
            primary_id_document_type_pk = primary_id_document_type_value
            
        try:
            # Retrieve the IdDocumentType instance
            id_document_type_instance = IdDocumentType.objects.get(pk=primary_id_document_type_pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid primary_id_document_type ID.")
        
        instance = ClientDetails.objects.create(**validated_data, primary_id_document_type=id_document_type_instance)
        
        return instance
