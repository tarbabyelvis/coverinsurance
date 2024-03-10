import json
import logging
from django.db import transaction
from django.forms import ValidationError
import openpyxl
from typing import Any, Dict, List
from clients.models import ClientDetails
from clients.serializers import ClientDetailsSerializer
from core.utils import get_dict_values, replace_keys
from policies.models import Policy

logger = logging.getLogger(__name__)


@transaction.atomic
def upload_clients_and_policies(
    file_obj: Any, client_columns: List, policy_columns
) -> None:
    # Convert received column definitions from JSON strings
    received_policy_columns = json.loads(policy_columns)
    received_client_columns = json.loads(client_columns)

    # Merge client and policy column definitions
    merged_columns = {**received_client_columns, **received_policy_columns}

    # Load the Excel workbook
    wb = openpyxl.load_workbook(file_obj.file)

    # Extract expected column headers for clients and policies
    expected_client_headers: List[str] = get_dict_values(received_client_columns)
    expected_policy_headers: List[str] = get_dict_values(received_policy_columns)

    # Select the active worksheet
    ws = wb.active

    # Extract headers from the worksheet
    headers: List[str] = [cell.value.strip() for cell in ws[1]]

    # Check if expected headers are present in the worksheet
    expected_headers = expected_client_headers + expected_policy_headers
    if not set(expected_headers).issubset(set(headers)):
        raise ValidationError("Headers not matching the ones on the excel sheet")

    # Iterate over rows in the worksheet
    for row in ws.iter_rows(min_row=2, values_only=True):
        # Create dictionary mapping headers to row values
        row_dict: Dict[str, Any] = dict(zip(headers, row))
        # Replace column keys with expected keys
        row_dict = replace_keys(merged_columns, row_dict)

        # Extract client and policy data
        client_data = {k: row_dict[k] for k in received_client_columns}
        policy_data = {k: row_dict[k] for k in received_policy_columns}

        # Validate client data using serializer
        serializer = ClientDetailsSerializer(data=client_data)
        serializer.is_valid(raise_exception=True)

        # Create client and policy objects
        client = ClientDetails.objects.create(**client_data)
        Policy.objects.create(client=client, **policy_data)
