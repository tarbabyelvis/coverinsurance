# serializers.py
from datetime import datetime
from django.db import transaction
import json
from rest_framework import serializers
from clients.commons import CLIENTS_EXPECTED_COLUMNS
from .models import ClientDetails, ClientEmploymentDetails, IdDocumentType
from django.core.exceptions import ObjectDoesNotExist
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


class ClientEmploymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientEmploymentDetails
        exclude = ["client"]


class IdDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdDocumentType
        exclude = ["client"]


class ClientDetailsSerializer(serializers.ModelSerializer):
    employment_details = ClientEmploymentDetailsSerializer(many=True, required=False)

    class Meta:
        model = ClientDetails
        exclude = ["deleted"]
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
        # Convert QueryDict to a mutable dictionary
        mutable_data = data.copy()

        # Convert datetime to date for the 'date_of_birth' field if needed
        if "date_of_birth" in mutable_data and isinstance(
            mutable_data["date_of_birth"], datetime
        ):
            mutable_data["date_of_birth"] = mutable_data["date_of_birth"].date()

        if isinstance(mutable_data["primary_id_document_type"], IdDocumentType):
            # If the value is an instance of IdDocumentType, use it directly
            mutable_data["primary_id_document_type"] = mutable_data[
                "primary_id_document_type"
            ].pk

        elif isinstance(mutable_data["primary_id_document_type"], str):
            # If the value is a string, check if it's a number
            if mutable_data["primary_id_document_type"].isdigit():
                # If it's a number, retrieve the IdDocumentType instance using the primary key
                mutable_data["primary_id_document_type"] = IdDocumentType.objects.get(
                    pk=mutable_data["primary_id_document_type"]
                ).pk
            else:
                # If it's not a number, get the IdDocumentType instance using the name
                mutable_data["primary_id_document_type"] = IdDocumentType.objects.get(
                    type_name__iexact=mutable_data["primary_id_document_type"]
                ).pk

        else:
            # If it's already a primary key, retrieve the IdDocumentType instance using the primary key
            try:
                mutable_data["primary_id_document_type"] = IdDocumentType.objects.get(
                    pk=mutable_data["primary_id_document_type"]
                ).pk
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    "Invalid primary_id_document_type ID."
                )

        return super().to_internal_value(mutable_data)

    def validate(self, data):
        errors = {}

        # Iterate over each field in the serializer
        for field_name, value in data.items():
            # Get the corresponding model field
            model_field = self.fields[field_name]

            # Validate the data type
            try:
                # Attempt to convert the value to the correct data type
                if model_field.field_name == "date_of_birth" and isinstance(
                    value, datetime
                ):
                    # If the field is 'date_of_birth' and the value is datetime, cast it to date
                    data[field_name] = value.date()
                else:
                    data[field_name] = model_field.to_internal_value(value)
            except serializers.ValidationError as e:
                print("Error with datatypes")
                errors[field_name] = e.detail

        if errors:
            print("Error validation")
            raise serializers.ValidationError(errors)
        print("Done validation")
        return data

    @transaction.atomic
    def create(self, validated_data):
        print("trying to create")
        employment_details_data = validated_data.pop("employment_details", [])
        # Extract the nested IdDocumentType data from the validated data
        primary_id_document_type_value = validated_data.pop("primary_id_document_type")

        # Initialize variable to hold IdDocumentType instance
        id_document_type_instance = None

        try:
            if isinstance(primary_id_document_type_value, IdDocumentType):
                # If the value is an instance of IdDocumentType, use it directly
                id_document_type_instance = primary_id_document_type_value
            elif isinstance(primary_id_document_type_value, str):
                # If the value is a string, check if it represents a digit
                if primary_id_document_type_value.isdigit():
                    # If it's a digit, retrieve the IdDocumentType instance using the primary key
                    id_document_type_instance = IdDocumentType.objects.get(
                        pk=primary_id_document_type_value
                    )
                else:
                    # If it's not a digit, get the IdDocumentType instance using the name
                    id_document_type_instance = IdDocumentType.objects.get(
                        type_name__iexact=primary_id_document_type_value
                    )
            else:
                # If it's already a primary key, retrieve the IdDocumentType instance using the primary key
                id_document_type_instance = IdDocumentType.objects.get(
                    pk=primary_id_document_type_value
                )
        except IdDocumentType.DoesNotExist:
            # Handle the case where the IdDocumentType instance does not exist
            raise serializers.ValidationError("Invalid primary_id_document_type value.")

        # Cast date_of_birth value to date if it's datetime
        if "date_of_birth" in validated_data and isinstance(
            validated_data["date_of_birth"], datetime
        ):
            validated_data["date_of_birth"] = validated_data["date_of_birth"].date()

        # Create the ClientDetails instance
        instance = ClientDetails.objects.create(
            **validated_data, primary_id_document_type=id_document_type_instance
        )

        # Create the ClientEmploymentDetails instances
        for employment_detail_data in employment_details_data:
            ClientEmploymentDetails.objects.create(
                client=instance, **employment_detail_data
            )

        return instance


class ExcelSchema(Schema):
    file = fields.Field(required=True)
    columns = fields.List(fields.String(), required=True)
    # columns = fields.Dict(required=True, keys=fields.String(), values=fields.String())

    @validates_schema
    def validate_excel_file(self, data, **kwargs):
        if not data.get("file"):
            raise ValidationError("Excel file is required.")

        filename = data["file"][0]
        if not filename.name.lower().endswith(".xlsx"):
            raise ValidationError("File must be in Excel format (xlsx).")

        if not in_memory_file_exists(filename):
            raise ValidationError("File does not exist.")

        # expected columns
        received_columns = json.loads(data["columns"][0])

        # convert to dict

        actual_columns = list(received_columns.keys())
        missing_columns = [
            col for col in CLIENTS_EXPECTED_COLUMNS if col not in actual_columns
        ]
        unexpected_columns = [
            col for col in actual_columns if col not in CLIENTS_EXPECTED_COLUMNS
        ]

        if missing_columns:
            raise ValidationError(f'Missing columns: {", ".join(missing_columns)}')

        if unexpected_columns:
            raise ValidationError(
                f'Unexpected columns: {", ".join(unexpected_columns)}'
            )

        print("first serializer done")
