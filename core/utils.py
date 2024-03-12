from typing import List


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
