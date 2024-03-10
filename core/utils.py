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
