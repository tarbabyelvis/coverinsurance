def bordrex_report_util(data_list):
    flattened_data = []
    for item in data_list:
        flattened_item = {
            "policy_id": item["id"],
            "policy_number": item["policy_number"],
            "client_id": item["client"]["id"],
            "first_name": item["client"]["first_name"],
            "last_name": item["client"]["last_name"],
            "primary_id_number": item["client"]["primary_id_number"],
            "external_id": item["client"]["external_id"],
            "entity_type": item["client"]["entity_type"],
            "gender": item["client"]["gender"],
            "date_of_birth": item["client"]["date_of_birth"],
            "phone_number": item["client"]["phone_number"],
            "address_street": item["client"]["address_street"],
            "address_province": item["client"]["address_province"],
            "insurer_name": item["insurer"]["name"],
            "created": item["created"],
            "updated": item["updated"],
            "commencement_date": item["commencement_date"],
            "policy_term": item["policy_term"],
            "sum_insured": item["sum_insured"],
            "expiry_date": item["expiry_date"],
            "sum_insured": item["sum_insured"],
            "total_premium": item["total_premium"],
            "business_unit": item["business_unit"],
            "policy_status": item["policy_status"],
            "premium_frequency": item["premium_frequency"],
            "commission_amount": item["commission_amount"],
            "admin_fee": item["admin_fee"],
        }
        flattened_data.append(flattened_item)
    return flattened_data
