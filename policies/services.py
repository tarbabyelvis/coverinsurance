import json
import logging
from django.db import transaction
from django.forms import ValidationError
import openpyxl
from typing import Any, Dict, List
from clients.models import ClientDetails
from clients.serializers import ClientDetailsSerializer
from core.utils import get_dict_values, merge_dict_into_another, replace_keys
from policies.constants import DEFAULT_CLIENT_FIELDS
from policies.models import Policy
from policies.serializers import PolicySerializer

logger = logging.getLogger(__name__)


@transaction.atomic
def upload_clients_and_policies(
    file_obj: Any, client_columns: List, policy_columns
) -> None:
    print("The columns loaded")
    # Convert received column definitions from JSON strings
    # received_policy_columns = json.loads(policy_columns)
    # received_client_columns = json.loads(client_columns)

    received_policy_columns = policy_columns
    received_client_columns = client_columns

    # Merge client and policy column definitions
    merged_columns = {**received_client_columns, **received_policy_columns}
    print("done merging")
    print(file_obj.file)

    # Load the Excel workbook
    wb = openpyxl.load_workbook(file_obj.file)

    # Extract expected column headers for clients and policies
    expected_client_headers: List[str] = get_dict_values(received_client_columns)
    expected_policy_headers: List[str] = get_dict_values(received_policy_columns)

    # Select the active worksheet
    ws = wb.active
    print("Workbook stage")
    print(ws)
    print("DOne")

    # Extract headers from the worksheet
    headers: List[str] = [cell.value.strip() for cell in ws[1]]
    print("Header done")

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
        client_data = merge_dict_into_another(client_data, DEFAULT_CLIENT_FIELDS)
        # check gender and replace string ('Unknown' for 'U', 'Male' for 'M', 'Female' for 'F')
        # if client_data["gender"] == "U":
        #     client_data["gender"] = "Unknown"
        # elif client_data["gender"] == "M":
        #     client_data["gender"] = "Male"
        # elif client_data["gender"] == "F":
        #     client_data["gender"] = "Female"
        if "gender" in client_data:
            gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}
            client_data["gender"] = gender_mapping.get(client_data["gender"], "Unknown")

        print(client_data)

        policy_data = {k: row_dict[k] for k in received_policy_columns}
        print(policy_data)

        # Validate client data using serializer
        serializer = ClientDetailsSerializer(data=client_data)
        print("done with the serializer")
        serializer.is_valid(raise_exception=True)
        client = ClientDetails.objects.create(**client_data)
        print("done creating client")

        # Create client and policy objects
        policy_serializer = PolicySerializer(data={**policy_data, "client": client})
        policy_serializer.is_valid(raise_exception=True)
        Policy.objects.create(client=client, **policy_data)
