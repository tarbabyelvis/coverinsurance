# serializers.py
from datetime import datetime
import json
from rest_framework import serializers
from clients.commons import CLIENTS_EXPECTED_COLUMNS
from .models import ClientDetails, IdDocumentType
from django.core.exceptions import ObjectDoesNotExist
import os
from marshmallow import Schema, fields, validates_schema, ValidationError


def in_memory_file_exists(in_memory_file):
    try:
        # Attempt to read a small chunk from the file-like object
        # This will fail if the file-like object is closed or empty
        in_memory_file.read(0)
        return True
    except (AttributeError, IOError):
        # If the file-like object is closed or empty, an exception will be raised
        return False

class ClientDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDetails
        exclude = ['deleted']
        # fields = [field.name for field in ClientDetails._meta.get_fields() if field.name != 'deleted']

    def validate_primary_id_document_type(self, value):
        print("validate primary ID")
        try:
            if isinstance(value, IdDocumentType):
                # If the value is an instance of IdDocumentType, use its primary key
                value = value.pk
            # Check if the provided ID exists in the IdDocumentType table
            # if string get using name
            if isinstance(value, str):
                value = IdDocumentType.objects.get(type_name__iexact=value).pk
            else:
                value = IdDocumentType.objects.get(pk=value).pk
        except ObjectDoesNotExist:
            # If the object does not exist, raise a validation error
            raise serializers.ValidationError("Invalid primary_id_document_type ID.")
        
        return value
    
    def to_internal_value(self, data):
        # Convert datetime to date for the 'date_of_birth' field if needed
        if 'date_of_birth' in data and isinstance(data['date_of_birth'], datetime):
            data['date_of_birth'] = data['date_of_birth'].date()

        if isinstance(data["primary_id_document_type"], IdDocumentType):
            # If the value is an instance of IdDocumentType, use it directly
            data["primary_id_document_type"] = data["primary_id_document_type"].pk
        elif isinstance(data["primary_id_document_type"], str):
            # If the value is a string, get the IdDocumentType instance using the name
            data["primary_id_document_type"] = IdDocumentType.objects.get(type_name__iexact=data["primary_id_document_type"]).pk

            print(data["primary_id_document_type"])
        else:
            # If it's already a primary key, retrieve the IdDocumentType instance using the primary key
            try:
                data["primary_id_document_type"] = IdDocumentType.objects.get(pk=data["primary_id_document_type"]).pk
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Invalid primary_id_document_type ID.")
        return super().to_internal_value(data)
    
    def validate(self, data):
        print("validate")
        errors = {}

        # Iterate over each field in the serializer
        for field_name, value in data.items():
            print("iteration")
            # Get the corresponding model field
            model_field = self.fields[field_name]

            # Validate the data type
            try:
                # Attempt to convert the value to the correct data type
                if model_field.field_name == 'date_of_birth' and isinstance(value, datetime):
                    # If the field is 'date_of_birth' and the value is datetime, cast it to date
                    data[field_name] = value.date()
                else:
                    data[field_name] = model_field.to_internal_value(value)
            except serializers.ValidationError as e:
                print("Error with datatypes")
                errors[field_name] = e.detail

        if errors:
            print('Error validation')
            raise serializers.ValidationError(errors)
        print("Done validation")
        return data


    def create(self, validated_data):
        print("Error Creating")
        # Extract the nested IdDocumentType data from the validated data
        primary_id_document_type_value = validated_data.pop('primary_id_document_type')
        
        # Initialize variable to hold IdDocumentType instance
        id_document_type_instance = None
        
        if isinstance(primary_id_document_type_value, IdDocumentType):
            # If the value is an instance of IdDocumentType, use it directly
            id_document_type_instance = primary_id_document_type_value
        elif isinstance(primary_id_document_type_value, str):
            # If the value is a string, get the IdDocumentType instance using the name
            id_document_type_instance = IdDocumentType.objects.get(type_name__iexact=primary_id_document_type_value)
        else:
            # If it's already a primary key, retrieve the IdDocumentType instance using the primary key
            try:
                id_document_type_instance = IdDocumentType.objects.get(pk=primary_id_document_type_value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Invalid primary_id_document_type ID.")

        # Cast date_of_birth value to date if it's datetime
        if 'date_of_birth' in validated_data and isinstance(validated_data['date_of_birth'], datetime):
            validated_data['date_of_birth'] = validated_data['date_of_birth'].date()
            print(validated_data['date_of_birth'])

        # Create the ClientDetails instance
        instance = ClientDetails.objects.create(**validated_data, primary_id_document_type=id_document_type_instance)
        
        return instance



class ExcelSchema(Schema):
    file = fields.Field(required=True)
    columns = fields.List(fields.String(), required=True)
    # columns = fields.Dict(required=True, keys=fields.String(), values=fields.String())

    @validates_schema
    def validate_excel_file(self, data, **kwargs):
        if not data.get('file'):
            raise ValidationError('Excel file is required.')

        filename = data['file'][0]
        if not filename.name.lower().endswith('.xlsx'):
            raise ValidationError('File must be in Excel format (xlsx).')

        if not in_memory_file_exists(filename):
            raise ValidationError('File does not exist.')

        # expected columns
        received_columns = json.loads(data['columns'][0])

        # convert to dict

        
        actual_columns = list(received_columns.keys())
        missing_columns = [col for col in CLIENTS_EXPECTED_COLUMNS if col not in actual_columns]
        unexpected_columns = [col for col in actual_columns if col not in CLIENTS_EXPECTED_COLUMNS]

        if missing_columns:
            raise ValidationError(f'Missing columns: {", ".join(missing_columns)}')

        if unexpected_columns:
            raise ValidationError(f'Unexpected columns: {", ".join(unexpected_columns)}')
        
        print("first serializer done")

