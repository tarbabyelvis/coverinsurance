from typing import List
from django.db import connection
from datetime import date, datetime, timedelta
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 20  # Set your desired page size here
    page_size_query_param = "page_size"
    max_page_size = 1000  # Optionally set a maximum page size


def get_dict_values(input_dict) -> List:
    non_empty_values = []
    for key, value in input_dict.items():
        if value:  # Check if the value is not empty
            non_empty_values.append(value)
    return non_empty_values


def replace_keys(dict1, dict2):
    new_dict2 = {}
    for key, value in dict2.items():
        if key in dict1.values():
            new_key = [k for k, v in dict1.items() if v == key][0]
            new_dict2[new_key] = value
        else:
            new_dict2[key] = value
    return new_dict2


def merge_dict_into_another(dict1, dict2):
    for key, value in dict2.items():
        if key not in dict1:
            dict1[key] = value
    return dict1


def construct_client_data(row_dict, received_client_columns, DEFAULT_CLIENT_FIELDS):
    if not isinstance(received_client_columns, dict) or not isinstance(row_dict, dict):
        raise ValueError("received_client_columns and row_dict must be dictionaries")

    client_data = {k: row_dict[k] for k in received_client_columns if k in row_dict}
    client_data = merge_dict_into_another(client_data, DEFAULT_CLIENT_FIELDS)
    return client_data


def check_dict_has_key(dictionary, key):
    """
    Check if a key exists in a dictionary.

    Args:
        dictionary (dict): The dictionary to be checked.
        key: The key to be checked for existence.

    Returns:
        bool: True if the key exists in the dictionary, False otherwise.
    """
    return key in dictionary


def check_gender(dictionary):
    """
    Check the value of 'gender' in a dictionary and return the corresponding gender string.

    Args:
        dictionary (dict): The dictionary containing the 'gender' key.

    Returns:
        str: The corresponding gender string ('Unknown' for 'U', 'Male' for 'M', 'Female' for 'F').
    """
    gender_mapping = {"U": "Unknown", "M": "Male", "F": "Female"}
    gender_value = dictionary.get("gender", "U")
    return gender_mapping.get(gender_value, "Unknown")


def convert_to_datetime(date_string):
    # List of known datetime formats
    date_formats = [
        "%m/%d/%Y %I:%M:%S %p",  # MM/DD/YYYY HH:MM:SS AM/PM
        "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
        "%d-%m-%Y %H:%M:%S",  # DD-MM-YYYY HH:MM:SS
        "%Y/%m/%d %H:%M:%S",  # YYYY/MM/DD HH:MM:SS
        "%m/%d/%Y",  # MM/DD/YYYY
        "%Y-%m-%d",  # YYYY-MM-DD
        "%d-%m-%Y",  # DD-MM-YYYY
        "%Y/%m/%d",  # YYYY/MM/DD
    ]

    # Try to convert the date string to datetime object using each format
    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            pass  # If conversion fails, try the next format

    # If none of the formats work, return None
    return None


def serialize_dates(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        serialized_dict = {}
        for key, value in obj.items():
            serialized_dict[key] = serialize_dates(value)
        return serialized_dict
    elif isinstance(obj, list):
        return [serialize_dates(item) for item in obj]
    else:
        return obj


def get_current_schema():
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        row = cursor.fetchone()
    return row[0] if row else None


def first_day_of_previous_month():
    return last_day_of_previous_month().replace(day=1)


def last_day_of_previous_month():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    return first_day_of_current_month - timedelta(days=1)


def get_initial_letter(word: str):
    if word:
        return word[0]
    return ""


def get_loan_id_from_legacy_loan(loan_external_id: str):
    if "_" in loan_external_id:
        legacy_loan_id = loan_external_id.split('_')[1]
        return legacy_loan_id
    return loan_external_id


def generate_policy_number() -> str:
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S")
