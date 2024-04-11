POLICY_COLUMNS = {
    "json_ref_id": "Ref Id",
    "json_batch_ref": "Batch Ref",
    "created": "Create Date",
    "policy_number": "Loan Ref",
    "policy_status": "Policy Status",
    "commencement_date": "Policy Commencement Date",
    "expiry_date": "Policy Expiry Date",
    "policy_term": "Term Of Policy",
    "json_new_policy_indicator": "New Policy Indicator",
    "json_sales_channel": "Sales Channel",
    "json_death_premium": "Death Premium",
    "json_PTD_premium": "PTDPremium",
    "sum_insured": "Original Loan Balance",
    "json_retrenchment_premium": "Retrenchment Premium",
    "json_death_original_sum_assured": "Death Original Sum Assured",
    "json_death_current_sum_assured": "Death Current Sum Assured",
    "json_ptd_current_sum_assured": "PTDCurrent Sum Assured",
    "json_retrenchment_current_sum_assured": "Retrenchment Current Sum Assured",
    "json_total_policy_premium_collected": "Total Policy Premium Collected",
    "total_premium": "Total Policy Premium Payable",
    "json_current_outstanding_balance": "Current Outstanding Balance",
    "json_instalment_amount": "Installment Amount",
    "json_ptd_original_sum_insured": "PTDOriginal Sum Assured",
    "json_retrenchment_sum_insured": "Retrenchment Original Sum Assured",
    "json_income_group": "Income Group",
    "admin_fee": "Admin Binder Fees",
    "commission": "Commission",
}

CLIENT_COLUMNS = {
    "last_name": "Principal Surname",
    "first_name": "Principal First Name",
    "middle_name": "Principal Initials",
    "primary_id_number": "Principal ID",
    "gender": "Principal Gender",
    "date_of_birth": "Principal Date Of Birth",
    "address_street": "Principal Member Physical Address",
    "email": "Principal Member Email Address",
    "phone_number": "Principal Telephone Number",
    "postal_code": "Postal Code",
}

POLICY_COLUMNS_BORDREX = {
    "json_administrator_identifier": "Administrator identifier",
    "business_unit": "Division",
    "risk_identifier": "Risk Identifier",
    "json_sub_scheme_name": "Sub Scheme Name",
    "policy_number": "Policy Number",
    "commencement_date": "Policy Commencement date",
    "expiry_date": "Policy Expiry Date",
    "policy_term": "Term of policy",
    "total_premium": "Prem",
    "json_premium_pd": "Prem Pd",
    "commission_amount": "Commission",
    "json_binder_fee": "Binder Fee",
    "json_net_premium_paid_including_admin": "Net premium paid over to GR including GR admin fee",
    "admin_fee": "GR Admin Fee",
    "premium_frequency": "Premium Frequency",
    "json_death_indicator": "Death indicator",
    "json_ptd_indicator": "PTD indicator",
    "json_ttd_indicator": "TTD indicator",
    "json_retrenchment_indicator": "Retrenchment indicator",
    "json_dread_disease_indicator": "Dread disease indicator",
    "identify_theft_indicator": "Identity theft indicator",
    "json_accident_death_indicator": "Accidental death indicator",
    "sum_insured": "Original loan balance",
    "json_current_loan_balance": "Current outstanding balance",
    "json_instalment_amount": "Instalment amount",
    "policy_status": "policy_status",
}

CLIENT_COLUMNS_BORDREX = {
    "last_name": "Life 1 Surname",
    "first_name": "Life 1 first name",
    "middle_name": "Life 1 Initials",
    "primary_id_number": "Life 1 ID",
    "gender": "Life 1 Gender",
    "date_of_birth": "Date Of Birth",
    "external_id": "Client Identifier",
    "address_street": "address1",
    "address_suburb": "address2",
    "address_province": "address3",
    "postal_code": "Postal Code",
    "phone_number": "Life 1 Telephone",
}

DEFAULT_CLIENT_FIELDS = {"primary_id_document_type": 1, "entity_type": "Individual"}

DEFAULT_POLICY_FIELDS = {"insurer": 1}

STATUS_MAPPING = {
    "Active": "A",
    "Lapsed": "L",
    "Cancelled": "X",
    "Expiry": "E",
    "Claimed": "C",
    "Reinstated": "R",
    "Not Taken Up": "N",
    "Paid Up": "P",
    "Surrendered": "S",
    "Surrendered due to replacement": "SR",
    "Transferred out": "T",
}


# Repayment Columns Mapping
REPAYMENT_COLUMNS = {
    "policy_id": "LoanNo",
    "payment_date": "LoanAdvanceDate",
    "amount": "PremiumAmount",
    "payment_reference": "Receipt"
}