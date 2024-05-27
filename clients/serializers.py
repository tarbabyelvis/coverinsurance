# serializers.py
from datetime import datetime
from django.db import transaction
import json
from rest_framework import serializers
from clients.commons import CLIENTS_EXPECTED_COLUMNS
from config.models import BusinessSector
from config.serializers import BusinessSectorSerializer
from .models import ClientDetails, ClientEmploymentDetails, IdDocumentType
from django.core.exceptions import ObjectDoesNotExist
from marshmallow import Schema, fields, validates_schema, ValidationError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


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
    sector = serializers.PrimaryKeyRelatedField(
        queryset=BusinessSector.objects.all(),
        required=False,
    )

    class Meta:
        model = ClientEmploymentDetails
        exclude = ["client"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print('instance ::')
        print(instance)
        return representation

    def to_internal_value(self, data):
        data = data.copy()
        sector_data = data.pop("sector", None)
        client_id = data.pop("client", None)
        instance = super().to_internal_value(data)
        if client_id is not None:
            instance["client"] = id
        if sector_data is not None:
            try:
                if isinstance(sector_data, int):
                    instance["sector"] = BusinessSector.objects.get(
                        id=sector_data)
                elif isinstance(sector_data, str):
                    instance["sector"] = BusinessSector.objects.get(
                        sector__iexact=sector_data
                    )
                else:
                    instance["sector"] = sector_data

            except BusinessSector.DoesNotExist:
                raise serializers.ValidationError(
                    "Invalid business sector value.")

        return instance

    @transaction.atomic
    def create(self, validated_data):
        sector = validated_data.pop("sector", None)
        if isinstance(sector, int):
            sector = BusinessSector.objects.get(id=sector)
            validated_data["sector"] = sector
        else:
            validated_data["sector"] = sector

        instance = ClientEmploymentDetails.objects.create(**validated_data)
        return instance
    
    def get_employment_details(self, obj):
        employment_details = ClientEmploymentDetails.objects.filter(client=obj).first()
        if employment_details:
            return ClientEmploymentDetailsSerializer(employment_details).data
        return None


class IdDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdDocumentType
        exclude = ["client"]


class ClientDetailsSerializer(serializers.ModelSerializer):
    employment_details = ClientEmploymentDetailsSerializer(required=False)

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
        print(data)
        mutable_data = data.copy()

        # Convert datetime to date for the 'date_of_birth' field if needed
        if "date_of_birth" in mutable_data and isinstance(
                mutable_data["date_of_birth"], datetime
        ):
            mutable_data["date_of_birth"] = mutable_data["date_of_birth"].date()

        if "primary_id_document_type" in mutable_data and isinstance(
                mutable_data["primary_id_document_type"], IdDocumentType
        ):
            # If the value is an instance of IdDocumentType, use it directly
            mutable_data["primary_id_document_type"] = mutable_data[
                "primary_id_document_type"
            ].pk

        elif "primary_id_document_type" in mutable_data and isinstance(
                mutable_data["primary_id_document_type"], str
        ):
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
            print("We are validating the id number")
            # If it's already a primary key, retrieve the IdDocumentType instance using the primary key
            try:
                if "primary_id_document_type" in mutable_data:
                    mutable_data["primary_id_document_type"] = (
                        IdDocumentType.objects.get(
                            pk=mutable_data["primary_id_document_type"]
                        ).pk
                    )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    "Invalid primary_id_document_type ID."
                )

        return super().to_internal_value(mutable_data)

    def validate(self, data):
        errors = {}

        # Define fields that should not be None
        non_nullable_fields = [
            "first_name",
            "last_name",
            "primary_id_number",
            "primary_id_document_type",
            "entity_type",
            "gender",
        ]  # Add your field names here

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
                    if model_field.field_name == "date_of_birth" and isinstance(
                            value, datetime
                    ):
                        # If the field is 'date_of_birth' and the value is datetime, cast it to date
                        data[field_name] = value.date()
                    elif model_field.field_name == "email":
                        # Validate email field
                        validate_email(value)
                    else:
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
        print("Done validation")
        return data

    @transaction.atomic
    def create(self, validated_data):
        employment_details_data = validated_data.pop("employment_details", None)
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
        if employment_details_data:
            ClientEmploymentDetails.objects.create(
                client=instance, **employment_details_data
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