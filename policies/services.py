import logging
from django.db import transaction
from django.forms import ValidationError
import openpyxl
from typing import Any, Dict, List
from core.utils import get_dict_values, merge_dict_into_another, replace_keys
from policies.constants import DEFAULT_CLIENT_FIELDS, DEFAULT_POLICY_FIELDS
from policies.serializers import ClientPolicyRequestSerializer

logger = logging.getLogger(__name__)


def extract_json_fields(dictionary):
    policy_details = {}

    for key in list(dictionary.keys()):
        if key.startswith("json_"):
            new_key = key.replace("json_", "")
            policy_details[new_key] = dictionary.pop(key)

    dictionary["policy_details"] = policy_details
    return dictionary


@transaction.atomic
def upload_clients_and_policies(
        file_obj: Any, client_columns: List, policy_columns, source
) -> None:
    print("The columns loaded")
    # Convert received column definitions from JSON strings
    # received_policy_columns = json.loads(policy_columns)
    # received_client_columns = json.loads(client_columns)

    policy_type = None
    if source == "guardrisk":
        policy_type = 1
    elif source == "bordrex":
        policy_type = 1

    received_policy_columns = policy_columns
    received_client_columns = client_columns

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
        client_data = merge_dict_into_another(client_data, DEFAULT_CLIENT_FIELDS)

        if "gender" in client_data:
            gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}
            client_data["gender"] = gender_mapping.get(client_data["gender"], "Unknown")

        policy_data = {k: row_dict[k] for k in received_policy_columns}

        policy_data = merge_dict_into_another(policy_data, DEFAULT_POLICY_FIELDS)
        # convert all fields that have json prefix
        policy_data = extract_json_fields(policy_data)
        if policy_type is not None:
            policy_data["policy_type"] = policy_type

        serializer = ClientPolicyRequestSerializer(
            data={"client": client_data, "policy": policy_data},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()


@transaction.atomic
def upload_funeral_clients_and_policies(
        file_obj: Any, client_columns: List, policy_columns: List, source: str
) -> None:
    wb = openpyxl.load_workbook(file_obj.file)

    process_worksheet(wb, "Members", client_columns, "client")
    process_worksheet(wb, "Funeral All", policy_columns, "policy")


def extract_funeral_json_fields(dictionary):
    details = {}
    for key in list(dictionary.keys()):
        if key.startswith("json_"):
            new_key = key.replace("json_", "")
            details[new_key] = dictionary.pop(key)

    if "policy_number" in dictionary:
        dictionary["policy_details"] = details
        return dictionary
    else:
        dictionary["client_details"] = details
        return dictionary


def process_worksheet(
        wb: openpyxl.Workbook, worksheet_name: str, columns: List[str], data_type: str
) -> None:
    worksheet = wb[worksheet_name]
    headers = [cell.value.strip() for cell in worksheet[1]]
    expected_headers = get_dict_values(columns)

    if not set(expected_headers).issubset(set(headers)):
        raise ValidationError(f"{data_type.capitalize()} headers not matching the ones on the excel sheet")

    for row in worksheet.iter_rows(min_row=2, values_only=True):
        row_dict = dict(zip(headers, row))
        row_dict = replace_keys(columns, row_dict)

        data = {k: row_dict[k] for k in columns}
        data = merge_dict_into_another(data, DEFAULT_CLIENT_FIELDS if data_type == "client" else DEFAULT_POLICY_FIELDS)
        data = extract_funeral_json_fields(data)
        process_data(data, data_type)


def process_data(data: Dict[str, Any], data_type: str) -> None:
    if data_type == "client":
        process_client_data(data)
    elif data_type == "policy":
        process_policy_data(data)
    else:
        logger.warning(f"Unknown data type: {data_type}")


def process_client_data(client_data: Dict[str, Any]) -> None:
    gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}
    client_data["gender"] = gender_mapping.get(client_data.get("gender"), "Unknown")
    # Further processing if needed
    save_data(client_data, "client")


def process_policy_data(policy_data: Dict[str, Any]) -> None:
    # Further processing if needed
    save_data(policy_data, "policy")


def save_data(data: Dict[str, Any], data_type: str) -> None:
    # Implement serialization and saving logic here
    logger.info(f"Saving {data_type}: {data}")
    # Example: serializer.save()
