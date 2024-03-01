
import logging
from django.db import transaction
from django.forms import ValidationError
import openpyxl
import uuid
from typing import Any, Dict, List
from clients.models import ClientDetails
from django.core.files.uploadedfile import UploadedFile
from rest_framework.serializers import ValidationError as DRFValidationError
from clients.serializers import ClientDetailsSerializer

logger = logging.getLogger(__name__)


def upload_clients(file_obj) -> None:
    wb = openpyxl.load_workbook(file_obj.file)
    print("After processing")
    excel_file_name: str = file_obj.name
    print("Excel file name is:", excel_file_name)

    # Select the first worksheet
    ws = wb.active

    # Define expected headers
    expected_headers: List[str] = [
        "First Name", "Middlename", "Last Name", "ID Number", "ID Type",
        "Entity Type", "Gender", "Marital Status", "Date of Birth",
        "Email", "Phone number", "Address Street", "Address Suburb",
        "Address Town", "Address Province"
    ]

    # Get the headers from the worksheet
    headers: List[str] = [cell.value.strip() for cell in ws[1]]

    # Validate the headers
    if headers != expected_headers:
        raise ValidationError("Invalid excel format")

    # Create an empty list to store validated data
    validated_data_list: List[Dict[str, Any]] = []

    # Loop through the rows in the worksheet and validate each row using the serializer
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_dict: Dict[str, Any] = dict(zip(headers, row))
        print("The row: ", row_dict)
        serializer = ClientDetailsSerializer(data=row_dict)
        try:
            serializer.is_valid(raise_exception=True)
            validated_data_list.append(serializer.validated_data)
        except DRFValidationError as e:
            raise ValidationError(str(e))

    # Bulk create the objects within a transaction
    with transaction.atomic():
        ClientDetails.objects.bulk_create([
            ClientDetails(**validated_data) for validated_data in validated_data_list
        ])
