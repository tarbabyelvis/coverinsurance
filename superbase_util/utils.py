from supabase import create_client, Client
import requests
import json

from FinCover.settings import SUPABASE_REST_URL, SUPABASE_TOKEN, SUPABASE_URL

url: str = SUPABASE_REST_URL
key: str = SUPABASE_TOKEN
supabase: Client = create_client(url, key)
source: str = "fin_cover_admin"


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def convert_to_flattened_data(dictionary_list):
    flattened_data = []

    # Collecting columns dynamically
    columns = set()
    for item in dictionary_list:
        columns.update(item.keys())

    flattened_data.append(list(columns))  # Adding headers

    for item in dictionary_list:
        row = []
        for col in columns:
            value = item.get(col, "")
            if isinstance(value, dict) or isinstance(value, list):
                # If the value is a dictionary or list, convert it to a string
                value = str(value)
            row.append(value)
        flattened_data.append(row)

    return flattened_data


def get_receipts_by_transaction_ref(transaction_ref: str, organisation_id: str):
    data = (
        supabase.table("repayment_transactions")
        .select("*, organisation!inner(organisation_id)")
        .match(
            {
                "organisation.organisation_id": organisation_id,
                "transaction_reference": transaction_ref,
            }
        )
        .execute()
    )
    return data



def get_loan_transaction(loan_id, transaction_id, tenant_id):
    jsonPayload = {"loan_id": loan_id, "transaction_id": transaction_id}
    response = requests.post(
        SUPABASE_URL + "/query-loan-transaction",
        json=jsonPayload,
        headers={
            "tenant-id": tenant_id,
            "source": "loantracker",
            "Authorization": "Bearer {}".format(SUPABASE_TOKEN),
        },
    )
    report = json.loads(response.text)["message"]["data"]
    return repor

