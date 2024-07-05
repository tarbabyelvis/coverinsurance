import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import openpyxl
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.forms import ValidationError

from clients.enums import MaritalStatus
from core.enums import PremiumFrequency
from core.utils import get_dict_values, merge_dict_into_another, replace_keys
from policies.constants import DEFAULT_CLIENT_FIELDS, DEFAULT_POLICY_FIELDS, CLIENT_COLUMNS_INDLU, POLICY_COLUMNS_INDLU
from policies.constants import FUNERAL_POLICY_BENEFICIARY_COLUMNS, \
    FUNERAL_POLICY_CLIENT_COLUMNS, DEFAULT_BENEFICIARY_FIELDS, POLICY_CLIENT_COLUMNS_INDLU
from policies.models import Policy
from policies.serializers import BeneficiarySerializer, PolicySerializer
from policies.serializers import ClientPolicyRequestSerializer, PremiumPaymentSerializer

logger = logging.getLogger(__name__)


def extract_json_fields(dictionary):
    policy_details = {}

    for key in list(dictionary.keys()):
        if key.startswith("json_"):
            new_key = key.replace("json_", "")
            policy_details[new_key] = dictionary.pop(key)

    dictionary["policy_details"] = policy_details
    return json.dumps(dictionary)


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
    print(f'active sheet: {ws}')

    # Extract headers from the worksheet
    headers: List[str] = [cell.value.strip() for cell in ws[1]]

    # Check if expected headers are present in the worksheet
    expected_headers = expected_client_headers + expected_policy_headers
    if not set(expected_headers).issubset(set(headers)):
        unique_to_list1 = set(headers) - set(expected_headers)
        unique_to_list2 = set(expected_headers) - set(headers)
        print(f'unique to list1: {unique_to_list1}')
        print(f'unique to list2: {unique_to_list2}')

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
            gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female", "Male": "Male", "Female": "Female"}
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
        file_obj: Any
) -> None:
    wb = openpyxl.load_workbook(file_obj.file)

    # with ThreadPoolExecutor() as executor:
    #     client_policy_future = executor.submit(process_worksheet, wb, "Funeral All", FUNERAL_POLICY_CLIENT_COLUMNS,
    #                                            "client_policy")
    #
    #     policy_beneficiary_future = executor.submit(process_worksheet, wb, "Beneficiary Details",
    #                                                 FUNERAL_POLICY_BENEFICIARY_COLUMNS,
    #                                                 "beneficiary")
    #
    #     client_policy_data = client_policy_future.result()
    #
    #     policy_beneficiary_data = policy_beneficiary_future.result()
    client_policy_data = process_worksheet(wb, "Funeral All", FUNERAL_POLICY_CLIENT_COLUMNS, "client_policy")

    policy_beneficiary_data = process_worksheet(wb, "Beneficiary Details", FUNERAL_POLICY_BENEFICIARY_COLUMNS,
                                                "beneficiary")

    client_policy_beneficiary_data = match_beneficiaries_to_policies(policy_beneficiary_data, client_policy_data)

    client_policy_beneficiary_dependents_data = extract_funeral_dependant_fields(client_policy_beneficiary_data)

    save_client_policy_beneficiary_dependents_data(client_policy_beneficiary_dependents_data)

    # save_policy_beneficiary_data(policy_beneficiary_data)


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
        return dictionary


def extract_funeral_dependant_fields(client_details) -> List[Dict[str, Any]]:
    client_policy_beneficiary_dependents = []
    for client in client_details:
        dependents_list = []
        added_dependents = set()
        added_spouses = set()
        for key, value in client["policy_details"].items():
            if key.startswith("dependent") and value != "" and value is not None:
                # Check if key starts with "dependent", value is not an empty string, and not None
                dependent_number = key.split("_")[1]  # Extract the dependent number from the key
                if dependent_number not in added_dependents:
                    date_of_birth_key = f"dependent_{dependent_number}_date_of_birth "
                    date_of_birth = client["policy_details"][date_of_birth_key]
                    if isinstance(date_of_birth, int):
                        date_of_birth = "1900-01-01"

                    if date_of_birth is not None:  # Check if date_of_birth is not None
                        gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}
                        dependent = {
                            "number": dependent_number,
                            "dependant_gender": gender_mapping.get(
                                client["policy_details"].get(f"dependent_{dependent_number}_gender "), "Unknown"),
                            "dependant_dob": parser.parse(str(date_of_birth)).strftime(
                                "%Y-%m-%d") if date_of_birth != "1900-01-01" else None,
                            "relationship": 1
                        }
                        dependents_list.append(dependent)
                        added_dependents.add(dependent_number)
            if key.startswith("spouse") and value != "" and value is not None:
                date_of_birth_key = f"spouse_firstname "
                spouse_name = client["policy_details"][date_of_birth_key]
                spouse_dob = client["policy_details"].get(f"spouse_date_of_birth ")
                if isinstance(spouse_dob, int):
                    spouse_dob = "1900-01-01"
                if spouse_name is not None and spouse_name not in added_spouses:  # Check if date_of_birth is not None
                    gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}
                    dependent = {
                        "dependant_name": str(client["policy_details"].get(f"spouse_firstname ")) + " " + str(
                            client["policy_details"].get(f"spouse_surname ")),
                        "dependant_gender": gender_mapping.get(client["policy_details"].get(f"spouse_gender "),
                                                               "Unknown"),
                        "dependant_dob": parser.parse(str(spouse_dob)).strftime(
                            "%Y-%m-%d") if spouse_dob != "1900-01-01" else None,
                        "relationship": 2
                    }
                    dependents_list.append(dependent)
                    added_spouses.add(spouse_name)

        # Print the list of dependents

        client["dependants"] = dependents_list
        client_policy_beneficiary_dependents.append(client)
    return client_policy_beneficiary_dependents


def process_worksheet(
        wb: openpyxl.Workbook, worksheet_name: str, columns: List[str], data_type: str
) -> List[Dict[str, Any]]:
    worksheet = wb[worksheet_name]
    print(f'worksheet name: {worksheet}')
    if worksheet.max_row < 1:
        raise ValidationError(f"The worksheet {worksheet_name} is empty or has no header row")
    headers = [cell.value.strip() for cell in worksheet[1] if cell.value]
    expected_headers = get_dict_values(columns)
    if not set(expected_headers).issubset(set(headers)):
        raise ValidationError(f"{data_type.capitalize()} headers not matching the ones on the excel sheet")

    processed_data = []

    for row in worksheet.iter_rows(min_row=2, values_only=True):
        if any(cell is not None for cell in row):
            row_dict = dict(zip(headers, row))
            row_dict = replace_keys(columns, row_dict)
            data = {k: row_dict[k] for k in columns if k in row_dict}
            if data_type == "client_policy":
                default_columns = {**DEFAULT_CLIENT_FIELDS, **DEFAULT_POLICY_FIELDS}
            elif data_type == "policy":
                default_columns = {**DEFAULT_POLICY_FIELDS, "entity": "Indlu", "product_name": "Indlu Credit Life",
                                   "sub_scheme": "Credit Life", "policy_name_policy": "CREDIT_LIFE",
                                   "commission_frequency": "Monthly",
                                   "premium_frequency": "Monthly",
                                   }
            elif data_type == "client":
                default_columns = {**DEFAULT_CLIENT_FIELDS}
            elif data_type == "repayment":
                default_columns = {}
            elif data_type == "policy_client_dump":
                default_columns = {**DEFAULT_CLIENT_FIELDS, **DEFAULT_POLICY_FIELDS}
            else:
                default_columns = DEFAULT_BENEFICIARY_FIELDS

            data = merge_dict_into_another(data, default_columns)
            # data = extract_funeral_json_fields(data)
            processed_data.append(process_data(data, data_type))
    return processed_data


def process_data(data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
    processed_data = None
    if data_type == "client_policy":
        processed_data = process_client_policy_data(data)
    elif data_type == "policy":
        processed_data = process_indlu_policy_data(data)
    elif data_type == "client":
        processed_data = process_indlu_client_data(data)
    elif data_type == "policy_client_dump":
        processed_data = process_indlu_policy_client_dump_data(data)
    elif data_type == "beneficiary":
        processed_data = process_beneficiary_data(data)
    elif data_type == "repayment":
        processed_data = process_indlu_repayment_data(data)
    else:
        logger.warning(f"Unknown data type: {data_type}")
    return processed_data


def process_indlu_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]:
    client = extract_employment_fields(client_data)
    # for detail in client_data:
    #     print(f'detail in for loop')
    #     if detail == "client_details":
    #         for client_detail in client_data[detail]:
    #             if isinstance(client_data[detail][client_detail], datetime.datetime):
    #                 client_data[detail][client_detail] = client_data[detail][client_detail].strftime('%Y-%m-%d')
    #     if isinstance(client_data[detail], datetime.datetime):
    #         client_data[detail] = client_data[detail].strftime('%Y-%m-%d')
    gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female", "Male": "Male", "Female": "Female"}
    client["gender"] = gender_mapping.get(client.get("gender"), "Unknown")

    # Further processing if needed
    return client


def extract_employment_fields(client_details):
    employment_fields = {
        'job_title',
        'sector',
        'employer',
        'employment_date',
        'employer_name',
        'gross_salary'
    }
    employment_data = {}
    for field in employment_fields:
        if field in client_details:
            employment_data[field] = client_details.pop(field)
            client_details['employment_details'] = employment_data
    return client_details


def process_indlu_policy_data(policy_data: Dict[str, Any]):
    # Further processing if needed
    frequency_map = {
        1: PremiumFrequency.MONTHLY,
        3: PremiumFrequency.QUARTERLY,
        12: PremiumFrequency.ANNUAL,
        6: PremiumFrequency.SEMI_ANNUAL,
        2: PremiumFrequency.BI_ANNUAL,
        0: PremiumFrequency.ONCE_OFF
    }
    policy_data["policy_term"] = 1 if policy_data["policy_term"] == 0 else policy_data[
        "policy_term"]

    policy_data["premium_frequency"] = frequency_map.get(policy_data["premium_frequency"],
                                                         PremiumFrequency.ONCE_OFF).value

    policy_data["commission_frequency"] = frequency_map.get(policy_data["commission_frequency"],
                                                            PremiumFrequency.ONCE_OFF).value
    __calculate_and_set_expiry_date(policy_data)
    extract_json_fields(policy_data)
    return policy_data


def process_indlu_policy_client_dump_data(policy_data: Dict[str, Any]):
    frequency_map = {
        1: PremiumFrequency.MONTHLY,
        3: PremiumFrequency.QUARTERLY,
        12: PremiumFrequency.ANNUAL,
        6: PremiumFrequency.SEMI_ANNUAL,
        2: PremiumFrequency.BI_ANNUAL,
        0: PremiumFrequency.ONCE_OFF
    }
    policy_data["policy_term"] = 1 if policy_data["policy_term"] == 0 else policy_data[
        "policy_term"]

    policy_data["premium_frequency"] = frequency_map.get(policy_data["premium_frequency"],
                                                         PremiumFrequency.ONCE_OFF).value

    policy_data["commission_frequency"] = frequency_map.get(policy_data["commission_frequency"],
                                                            PremiumFrequency.ONCE_OFF).value
    __calculate_and_set_expiry_date(policy_data)
    extract_json_fields(policy_data)
    return policy_data


def __calculate_and_set_expiry_date(policy_data: Dict[str, Any]):
    policy_term = int(policy_data["policy_term"])
    policy_data["expiry_date"] = policy_data["commencement_date"].date() + relativedelta(months=policy_term)


def process_indlu_repayment_data(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    # Further processing if needed
    print('further processing indlu repayment data')
    return payment_data


def process_beneficiary_data(beneficiary_data: Dict[str, Any]) -> Dict[str, Any]:
    # Further processing if needed

    beneficiary_data["beneficiary_name"] = str(beneficiary_data["beneficiary_first_name"]) + " " + str(
        beneficiary_data["beneficiary_last_name"])
    beneficiary_data["relationship"] = 1
    beneficiary_data.pop("beneficiary_first_name")
    beneficiary_data.pop("beneficiary_last_name")
    # policy_number = beneficiary_data["beneficiary_policy_number"]
    # try:
    #     policy = Policy.objects.filter(
    #         policy_number=policy_number
    #     )
    #     if not policy.exists():
    #         raise Exception(f"Policy {policy_number} does not exist")
    #
    #     beneficiary_data["policy_id"] = policy.get().id
    #
    # except Exception as e:
    #     logger.error(f"Policy with policy number {policy_number} not found: {e}")

    for detail in beneficiary_data:
        if isinstance(beneficiary_data[detail], datetime.datetime):
            beneficiary_data[detail] = beneficiary_data[detail].strftime('%Y-%m-%d')

    return beneficiary_data


def process_client_policy_data(client_policy_data: Dict[str, Any]) -> Dict[str, Any]:
    # Further processing if needed
    frequency_map = {
        1: PremiumFrequency.MONTHLY,
        3: PremiumFrequency.QUARTERLY,
        12: PremiumFrequency.ANNUAL,
        6: PremiumFrequency.SEMI_ANNUAL,
        2: PremiumFrequency.BI_ANNUAL,
        0: PremiumFrequency.ONCE_OFF
    }

    marital_status_map = {
        "N": MaritalStatus.SINGLE,
        "Y": MaritalStatus.MARRIED
    }

    dependants = []

    client_address = client_policy_data["address_street"].split(";")

    client_policy_data["address_street"] = client_address[0]

    client_policy_data["address_suburb"] = client_address[1]

    client_policy_data["address_town"] = client_address[2]

    client_policy_data["policy_term"] = 1 if client_policy_data["policy_term"] == 0 else client_policy_data[
        "policy_term"]

    client_policy_data["premium_frequency"] = frequency_map.get(client_policy_data["premium_frequency"],
                                                                PremiumFrequency.ONCE_OFF).value

    client_policy_data["commission_frequency"] = frequency_map.get(client_policy_data["commission_frequency"],
                                                                   PremiumFrequency.ONCE_OFF).value
    client_policy_data["marital_status"] = marital_status_map.get(client_policy_data["marital_status"],
                                                                  MaritalStatus.SINGLE).value

    gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}

    client_policy_data["gender"] = gender_mapping.get(client_policy_data.get("gender"), "Unknown")

    for detail in client_policy_data:
        if detail == "policy_details":
            for policy_detail in client_policy_data[detail]:
                if isinstance(client_policy_data[detail][policy_detail], datetime.datetime):
                    client_policy_data[detail][policy_detail] = client_policy_data[detail][policy_detail].strftime(
                        '%Y-%m-%d')
        if isinstance(client_policy_data[detail], datetime.datetime):
            client_policy_data[detail] = client_policy_data[detail].strftime('%Y-%m-%d')

    return client_policy_data


def save_policy_beneficiary(policy_beneficiary_data: Dict[str, Any]):
    # Filter out non-dictionary values and None values
    data = {
        key: value
        for key, value in policy_beneficiary_data.items()
        if isinstance(value, dict) and "policy_id" in value
    }

    serializer = BeneficiarySerializer(data=policy_beneficiary_data)
    serializer.is_valid(raise_exception=True)
    print("")
    serializer.save()
    logger.info(f"Saved Policy Beneficiary {policy_beneficiary_data}")


def match_members_to_policies(members, policies):
    matched_policies = []
    for policy in policies:
        member_client_reference = policies['client_id']
        for member in members:
            if member['client_id'] == member_client_reference:
                policy['client'] = [member]
                matched_policies.append(policy)
    return matched_policies


@transaction.atomic
def save_client_policy_beneficiary_dependents_data(client_policy_data: List[Dict[str, Any]]) -> None:
    for client in client_policy_data:
        save_client_policy(client)
    # with ThreadPoolExecutor(max_workers=20) as executor:
    #     futures = [executor.submit(save_client_policy, client) for client in client_policy_data]
    #
    #     # Wait for all futures to complete
    #     for future in futures:
    #         future.result()


@transaction.atomic
def save_policy_beneficiary_data(policy_beneficiary_data: List[Dict[str, Any]]) -> None:
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(save_policy_beneficiary, policy) for policy in policy_beneficiary_data]

        # Wait for all futures to complete
        for future in futures:
            future.result()


@transaction.atomic
def upload_bulk_repayments(
        file_obj: Any, repayment_columns
) -> None:
    print("The columns loaded")
    # Load the Excel workbook
    wb = openpyxl.load_workbook(file_obj.file)
    repayments = process_worksheet(wb, "Receipts", repayment_columns, "repayment")
    save_indlu_repayments_data(repayments)


@transaction.atomic
def save_indlu_repayments_data(repayments: List[Dict[str, Any]]) -> None:
    print('saving now repayments...')
    for repayment in repayments:
        policy = Policy.objects.filter(policy_number=repayment['policy_id'])
        # Raise an error so that it rows back the other transactions
        if not policy.exists():
            raise Exception(f"Policy {repayment['policy_id']} does not exist!")
        repayment["policy_id"] = policy.id
        serializer = PremiumPaymentSerializer(
            data=repayment
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()


@transaction.atomic
def upload_indlu_clients_and_policies(
        file_obj: Any
) -> None:
    wb = openpyxl.load_workbook(file_obj.file)
    clients = process_worksheet(wb, "Members", CLIENT_COLUMNS_INDLU, "client")
    policies = process_worksheet(wb, "Loans", POLICY_COLUMNS_INDLU, "policy")

    policy_clients_dump = process_worksheet(wb, "Data Dumb", POLICY_CLIENT_COLUMNS_INDLU, "policy_client_dump")
    updated_policies, updated_clients = match_policies_and_clients(policies, clients, policy_clients_dump)
    save_client_policy_members_data(updated_policies, updated_clients)
    print('we finished...')


def match_clients_to_policies(policies, clients):
    matched_policies = []
    for policy in policies:
        client_id = policy['client_id']
        for client in clients:
            if policy['client_id'] == client_id:
                if policy.get('client') is None:
                    policy['client'] = client
                    matched_policies.append(policy)
    return matched_policies


def match_policies_and_clients(policies, clients, policy_clients_dump):
    unmatched_policies_clients = []
    # Create dictionaries for quick lookup
    policy_dict = {policy["policy_id"]: policy for policy in policies}
    client_dict = {client["client_id"]: client for client in clients}

    # Iterate over the dump
    for entry in policy_clients_dump:
        policy_id = entry["policy_id"]
        client_id = entry["client_id"]

        # Check if the policy and client exist in the respective lists
        if policy_id in policy_dict and client_id in client_dict:
            # Update the existing policy and client with the dump data
            policy_dict[policy_id].update(entry)
            client_dict[client_id].update(entry)
        else:
            # If either policy or client does not exist, add the entry to unmatched list
            unmatched_policies_clients.append(entry)

    # Convert the dictionaries back to lists if needed
    updated_policies = list(policy_dict.values())
    updated_policies.append(unmatched_policies_clients)
    updated_clients = list(client_dict.values())
    return updated_policies, updated_clients


@transaction.atomic
def save_client_policy_members_data(policies, clients):
    for policy in policies:
        client_id = policy['client_id']
        for client in clients:
            if policy['client_id'] == client_id:
                serializer = ClientPolicyRequestSerializer(
                    data={"client": client, "policy": policy},
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                logger.info(f"Saved Client and Policy ")
                break


@transaction.atomic
def save_client_policy_members_receipts_cli_charges_data(client_policy_data: List[Dict[str, Any]]) -> None:
    for client in client_policy_data:
        save_client_policy(client)


def save_client_policy(client_policy_data):
    client = {key: client_policy_data.pop(key) for key in ["first_name",
                                                           "last_name",
                                                           "primary_id_number",
                                                           "gender",
                                                           "date_of_birth",
                                                           "email",
                                                           "phone_number",
                                                           "address_street",
                                                           "address_suburb",
                                                           "address_town",
                                                           "postal_code",
                                                           "marital_status",
                                                           "primary_id_document_type",
                                                           "entity_type"]}
    policy_details = client_policy_data["policy_details"]
    for key, value in policy_details.items():
        if isinstance(value, datetime.time):
            policy_details[key] = value.strftime("%H:%M:%S")
    # Serialize to JSON
    client_policy_data["policy_details"] = json.dumps(policy_details)

    serializer = ClientPolicyRequestSerializer(
        data={"client": client, "policy": client_policy_data},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info(f"Saved Client and Policy {client} {client_policy_data}")


def match_beneficiaries_to_policies(beneficiaries, policies):
    matched_policies = []
    for beneficiary in beneficiaries:
        beneficiary_policy_number = beneficiary['beneficiary_policy_number']

        for policy in policies:
            if policy['policy_number'] == beneficiary_policy_number:
                if policy.get('beneficiaries') is None:
                    policy['beneficiaries'] = [beneficiary]
                else:
                    policy['beneficiaries'].append(beneficiary)
                matched_policies.append(policy)

    return matched_policies
