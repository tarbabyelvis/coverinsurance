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

FUNERAL_POLICY_BENEFICIARY_COLUMNS = {
    "beneficiary_policy_number": "Policy Number",
    "beneficiary_dob": "Date Of Birth",
    "beneficiary_first_name": "First Name",
    "beneficiary_last_name": "Last Name",
    "beneficiary_phone": "Phone Number",
    "beneficiary_address_street": "Address",
    "relationship_id": "Relative ID"

}

FUNERAL_POLICY_CLIENT_COLUMNS = {
    # Policy specific details
    "policy_number": "policy_number",
    "product_name": "product_name",
    "commencement_date": "policy_commencement_date",
    "expiry_date": "policy_expiry_date",
    "policy_term": "term_of_policy",
    "policy_status": "policy_status",
    "premium_frequency": "premium_frequency",
    "commission_amount": "commission",
    "commission_frequency": "commission_frequency",
    "premium": "total_premium_payable",
    "total_premium": "total_premium",
    "sub_scheme": "sub_scheme_name",
    "business_unit": "administrator_identifier",
    "admin_fee": "management_fees",
    "sum_insured": "death_original_sum_insured",

    # Client specific details
    "first_name": "principal_firstname",
    "last_name": "principal_surname",
    "primary_id_number": "principal_id",
    "gender": "principal_gender",
    "date_of_birth": "principal_date_of_birth",
    "email": "principal_email",
    "phone_number": "principal_phone_number",
    "address_street": "principal_physical_address",
    "postal_code": "principal_postal_code",
    "marital_status": "spouse_indicator",
    "json_insurer_name": "insurer_name",
    "json_client_identifier": "client_identifier",
    "json_division_identifier": "division_identifier",
    "json_product_option": "product_option",
    "json_policy_status_date": "policy_status_date",
    "json_new_policy_indicator": "new_policy_indicator",
    "json_sales_channel": "sales_channel",
    "json_cancelled_by": "cancelled_by",
    "json_death_indicator": "death_indicator",
    "json_premium_type": "premium_type",
    "json_death_cover_structure": "death_cover_structure",
    "json_death_current_sum_insured": "death_current_sum_insured",
    "json_reinsurer_name": "reinsurer_name",
    "json_death_current_ri_sum_insured": "death_current_ri_sum_insured",
    "json_death_ri_premium": "death_ri_premium",
    "json_death_ri_percent": "death_ri_percent",
    "json_total_premium_collected": "total_premium_collected",
    "json_total_premium_subsidy": "total_premium_subsidy",
    "json_total_reinsurance_premium": "total_reinsurance_premium",
    "json_total_reinsurance_premium_payable": "total_reinsurance_premium_payable",
    "json_total_financial_reinsurance_cashflows": "total_financial_reinsurance_cashflows",
    "json_total_financial_reinsurance_payable": "total_financial_reinsurance_payable",
    "json_binder_fees": "binder_fees",
    "json_outsourcing_fees": "outsourcing_fees",
    "json_marketing_fees": "marketing_fees",
    "json_claims_handling_fees": "claims_handling_fees",
    "json_total_gross_claim_amount": "total_gross_claim_amount",
    "json_gross_claim_paid": "gross_claim_paid",
    "json_reinsurance_recoveries": "reinsurance_recoveries",
    "json_principal_initials": "principal_initials",
    "json_number_adult_dependants": "number_adult_dependants",
    "json_number_child_dependants": "number_child_dependants",
    "json_number_extended_family": "number_extended_family",
    "json_spouse_surname": "spouse_surname",
    "json_spouse_firstname": "spouse_firstname",
    "json_spouse_initials": "spouse_initials",
    "json_spouse_id": "spouse_id",
    "json_spouse_gender": "spouse_gender",
    "json_spouse_date_of_birth": "spouse_date_of_birth",
    "json_spouse_cover_amount": "spouse_cover_amount",
    "json_spouse_cover_commencement_date": "spouse_cover_commencement_date",
    "json_dependent_1_gender": "dependent_1_gender",
    "json_dependent_1_date_of_birth": "dependent_1_date_of_birth",
    "json_dependent_1_type": "dependent_1_type",
    "json_dependent_1_cover_amount": "dependent_1_cover_amount",
    "json_dependent_1_cover_commencement_date": "dependent_1_cover_commencement_date",
    "json_dependent_2_gender": "dependent_2_gender",
    "json_dependent_2_date_of_birth": "dependent_2_date_of_birth",
    "json_dependent_2_type": "dependent_2_type",
    "json_dependent_2_cover_amount": "dependent_2_cover_amount",
    "json_dependent_2_cover_commencement_date": "dependent_2_cover_commencement_date",
    "json_dependent_3_gender ": "dependent_3_gender",
    "json_dependent_3_date_of_birth ": "dependent_3_date_of_birth",
    "json_dependent_3_type": "dependent_3_type",
    "json_dependent_3_cover_amount": "dependent_3_cover_amount",
    "json_dependent_3_cover_commencement_date": "dependent_3_cover_commencement_date",
    "json_dependent_4_gender": "dependent_4_gender",
    "json_dependent_4_date_of_birth": "dependent_4_date_of_birth",
    "json_dependent_4_type": "dependent_4_type",
    "json_dependent_4_cover_amount": "dependent_4_cover_amount",
    "json_dependent_4_cover_commencement_date": "dependent_4_cover_commencement_date",
    "json_dependent_5_gender": "dependent_5_gender",
    "json_dependent_5_date_of_birth": "dependent_5_date_of_birth",
    "json_dependent_5_type": "dependent_5_type",
    "json_dependent_5_cover_amount": "dependent_5_cover_amount",
    "json_dependent_5_cover_commencement_date": "dependent_5_cover_commencement_date",
    "json_dependent_6_gender": "dependent_6_gender",
    "json_dependent_6_date_of_birth": "dependent_6_date_of_birth",
    "json_dependent_6_type": "dependent_6_type",
    "json_dependent_6_cover_amount": "dependent_6_cover_amount",
    "json_dependent_6_cover_commencement_date": "dependent_6_cover_commencement_date",
    "json_dependent_7_gender": "dependent_7_gender",
    "json_dependent_7_date_of_birth": "dependent_7_date_of_birth",
    "json_dependent_7_type": "dependent_7_type",
    "json_dependent_7_cover_amount": "dependent_7_cover_amount",
    "json_dependent_7_cover_commencement_date": "dependent_7_cover_commencement_date",
    "json_dependent_8_gender": "dependent_8_gender",
    "json_dependent_8_date_of_birth": "dependent_8_date_of_birth",
    "json_dependent_8_type": "dependent_8_type",
    "json_dependent_8_cover_amount": "dependent_8_cover_amount",
    "json_dependent_8_cover_commencement_date": "dependent_8_cover_commencement_date",
    "json_dependent_9_gender": "dependent_9_gender",
    "json_dependent_9_date_of_birth": "dependent_9_date_of_birth",
    "json_dependent_9_type": "dependent_9_type",
    "json_dependent_9_cover_amount": "dependent_9_cover_amount",
    "json_dependent_9_cover_commencement_date": "dependent_9_cover_commencement_date",
    "json_dpip": "dpip",
    "json_reference_number": "reference_number",
    "json_policy_start_date": "policy_start_date"

}

# FUNERAL_POLICY_CLIENT_COLUMNS = {
#     "first_name": "Principal Firstname",
#     "last_name": "Principal Surname",
#     "primary_id_number": "Principal ID",
#     "external_id": "ID",
#     "gender": "Principal Gender",
#     "date_of_birth": "Principal Date Of Birth",
#     "email": "Principal Email",
#     "phone_number": "Principal Phone Number",
#     "address_street": "Principal Physical Address",
#     "address_suburb": "Suburb",
#     "address_town": "City",
#     "address_province": "Province",
#     "postal_code": "Principal Postal Code",
#
#
#
#     "json_time_stamp": "Time Stamp",
#     # "json_id": "ID",
#     "json_policy_id": "Policy ID",
#     "json_report_period_start": "Report Period Start",
#     "json_report_period_end": "Report Period End",
#     "json_administrator_identifier": "Administrator Identifier",
#     "json_insurer_name": "Insurer Name",
#     "json_client_identifier": "Client Identifier",
#     "json_division_identifier": "Division Identifier",
#     "json_sub_scheme_name": "Sub Scheme Name",
#     "json_policy_number": "Policy Number",
#     "json_product_name": "Product Name",
#     "json_product_option": "Product Option",
#     "json_policy_commencement_date": "Policy Commencement Date",
#     "json_policy_expiry_date": "Policy Expiry Date",
#     "json_term_of_policy": "Term Of Policy",
#     "json_policy_status": "Policy Status",
#     "json_policy_status_date": "Policy Status Date",
#     "json_new_policy_indicator": "New Policy Indicator",
#     "json_sales_channel": "Sales Channel",
#     "json_cancelled_by": "Cancelled By",
#     "json_death_indicator": "Death Indicator",
#     "json_premium_frequency": "Premium Frequency",
#     "json_premium_type": "Premium Type",
#     "json_death_original_sum_insured": "Death Original Sum Insured",
#     "json_death_cover_structure": "Death Cover Structure",
#     "json_death_current_sum_insured": "Death Current Sum Insured",
#     "json_reinsurer_name": "Reinsurer Name",
#     "json_death_current_ri_sum_insured": "Death Current Ri Sum Insured",
#     "json_death_ri_premium": "Death Ri Premium",
#     "json_death_ri_percent": "Death Ri Percent",
#     "json_total_premium_collected": "Total Premium Collected",
#     "json_total_premium_payable": "Total Premium Payable",
#     "json_total_premium": "Total Premium",
#     "json_total_premium_subsidy": "Total Premium Subsidy",
#     "json_total_reinsurance_premium": "Total Reinsurance Premium",
#     "json_total_reinsurance_premium_payable": "Total Reinsurance Premium Payable",
#     "json_total_financial_reinsurance_cashflows": "Total Financial Reinsurance Cashflows",
#     "json_total_financial_reinsurance_payable": "Total Financial Reinsurance Payable",
#     "json_commission_frequency": "Commission Frequency",
#     "json_commission": "Commission",
#     "json_binder_fees": "Binder Fees",
#     "json_outsourcing_fees": "Outsourcing Fees",
#     "json_marketing_fees": "Marketing Fees",
#     "json_management_fees": "Management Fees",
#     "json_claims_handling_fees": "Claims Handling Fees",
#     "json_total_gross_claim_amount": "Total Gross Claim Amount",
#     "json_gross_claim_paid": "Gross Claim Paid",
#     "json_reinsurance_recoveries": "Reinsurance Recoveries",
#     # "json_principal_surname": "Principal Surname",
#     # "json_principal_firstname": "Principal Firstname",
#     "json_principal_initials": "Principal Initials",
#     # "json_principal_id": "Principal ID",
#     # "json_principal_gender": "Principal Gender",
#     # "json_principal_date_of_birth": "Principal Date Of Birth",
#     # "json_principal_physical_address": "Principal Physical Address",
#     "json_second_address": "Second Address",
#     # "json_suburb": "Suburb",
#     # "json_province": "Province",
#     # "json_city": "City",
#     # "json_principal_postal_code": "Principal Postal Code",
#     "json_dpip": "Dpip",
#     "json_reference_number": "Reference Number",
#     # "json_policy_start_date": "Policy Start Date",
#     # "json_principal_phone_number": "Principal Phone Number",
#     # "json_principal_email": "Principal Email",
#     "json_income_group": "Income Group",
#     "json_spouse_indicator": "Spouse Indicator",
#     "json_number_adult_dependants": "Number Adult Dependants",
#     "json_number_child_dependants": "Number Child Dependants",
#     "json_number_extended_family": "Number Extended Family",
#     "json_spouse_surname": "Spouse Surname",
#     "json_spouse_firstname": "Spouse Firstname",
#     "json_spouse_initials": "Spouse Initials",
#     "json_spouse_id": "Spouse ID",
#     "json_spouse_gender": "Spouse Gender",
#     "json_spouse_date_of_birth": "Spouse Date Of Birth",
#     "json_spouse_cover_amount": "Spouse Cover Amount",
#     "json_spouse_cover_commencement_date": "Spouse Cover Commencement Date",
#     "json_dependent_1_gender": "Dependent 1 Gender",
#     "json_dependent_1_date_of_birth": "Dependent 1 Date Of Birth",
#     "json_dependent_1_type": "Dependent 1 Type",
#     "json_dependent_1_cover_amount": "Dependent 1 Cover Amount",
#     "json_dependent_1_cover_commencement_date": "Dependent 1 Cover Commencement Date",
#     "json_dependent_2_gender": "Dependent 2 Gender",
#     "json_dependent_2_date_of_birth": "Dependent 2 Date Of Birth",
#     "json_dependent_2_type": "Dependent 2 Type",
#     "json_dependent_2_cover_amount": "Dependent 2 Cover Amount",
#     "json_dependent_2_cover_commencement_date": "Dependent 2 Cover Commencement Date",
#     "json_dependent_3_gender": "Dependent 3 Gender",
#     "json_dependent_3_date_of_birth": "Dependent 3 Date Of Birth",
#     "json_dependent_3_type": "Dependent 3 Type",
#     "json_dependent_3_cover_amount": "Dependent 3 Cover Amount",
#     "json_dependent_3_cover_commencement_date": "Dependent 3 Cover Commencement Date",
#     "json_dependent_4_gender": "Dependent 4 Gender",
#     "json_dependent_4_date_of_birth": "Dependent 4 Date Of Birth",
#     "json_dependent_4_type": "Dependent 4 Type",
#     "json_dependent_4_cover_amount": "Dependent 4 Cover Amount",
#     "json_dependent_4_cover_commencement_date": "Dependent 4 Cover Commencement Date",
#     "json_dependent_5_gender": "Dependent 5 Gender",
#     "json_dependent_5_date_of_birth": "Dependent 5 Date Of Birth",
#     "json_dependent_5_type": "Dependent 5 Type",
#     "json_dependent_5_cover_amount": "Dependent 5 Cover Amount",
#     "json_dependent_5_cover_commencement_date": "Dependent 5 Cover Commencement Date",
#     "json_dependent_6_gender": "Dependent 6 Gender",
#     "json_dependent_6_date_of_birth": "Dependent 6 Date Of Birth",
#     "json_dependent_6_type": "Dependent 6 Type",
#     "json_dependent_6_cover_amount": "Dependent 6 Cover Amount",
#     "json_dependent_6_cover_commencement_date": "Dependent 6 Cover Commencement Date",
#     "json_dependent_7_gender": "Dependent 7 Gender",
#     "json_dependent_7_date_of_birth": "Dependent 7 Date Of Birth",
#     "json_dependent_7_type": "Dependent 7 Type",
#     "json_dependent_7_cover_amount": "Dependent 7 Cover Amount",
#     "json_dependent_7_cover_commencement_date": "Dependent 7 Cover Commencement Date",
#     "json_dependent_8_gender": "Dependent 8 Gender",
#     "json_dependent_8_date_of_birth": "Dependent 8 Date Of Birth",
#     "json_dependent_8_type": "Dependent 8 Type",
#     "json_dependent_8_cover_amount": "Dependent 8 Cover Amount",
#     "json_dependent_8_cover_commencement_date": "Dependent 8 Cover Commencement Date",
#     "json_dependent_9_gender": "Dependent 9 Gender",
#     "json_dependent_9_date_of_birth": "Dependent 9 Date Of Birth",
#     "json_dependent_9_type": "Dependent 9 Type",
#     "json_dependent_9_cover_amount": "Dependent 9 Cover Amount",
#     "json_dependent_9_cover_commencement_date": "Dependent 9 Cover Commencement Date",
# }

# POLICY_COLUMNS_BORDREX = {
#     "json_administrator_identifier": "Administrator identifier",
#     "business_unit": "Division",
#     "risk_identifier": "Risk Identifier",
#     "json_sub_scheme_name": "Sub Scheme Name",
#     "policy_number": "Policy Number",
#     "commencement_date": "Policy Commencement date",
#     "expiry_date": "Policy Expiry Date",
#     "policy_term": "Term of policy",
#     "total_premium": "Prem",
#     "json_premium_pd": "Prem Pd",
#     "commission_amount": "Commission",
#     "json_binder_fee": "Binder Fee",
#     "json_net_premium_paid_including_admin": "Net premium paid over to GR including GR admin fee",
#     "admin_fee": "GR Admin Fee",
#     "premium_frequency": "Premium Frequency",
#     "json_death_indicator": "Death indicator",
#     "json_ptd_indicator": "PTD indicator",
#     "json_ttd_indicator": "TTD indicator",
#     "json_retrenchment_indicator": "Retrenchment indicator",
#     "json_dread_disease_indicator": "Dread disease indicator",
#     "identify_theft_indicator": "Identity theft indicator",
#     "json_accident_death_indicator": "Accidental death indicator",
#     "sum_insured": "Original loan balance",
#     "json_current_loan_balance": "Current outstanding balance",
#     "json_instalment_amount": "Instalment amount",
#     "policy_status": "policy_status",
# }

POLICY_COLUMNS_BORDREX = {
    "policy_number": "LoanRefId",
    "client_id": "ClientRefId",
    "merchant": "Merchant",
    "province": "Province",
    "risk_identifier": "RiskBand",
    "credit_score": "ApplicationCreditScore",
    "sum_insured": "LoanAmount",
    "interest_rate": "InterestRate",
    "initiation_fee": "InitiationFee",
    "service_fee": "ServiceFee",
    "policy_term": "LoanTerm",
    "approval_date": "ApprovalDate",
    "commencement_date": "DisbursementDate",
    "policy_status": "LoanStatus",
    "debt_book": "DebtBook",
    "payment_method": "PaymentMethod",
    "expiry_date": "CloseDate",
}

POLICY_COLUMNS_INDLU = {
    "policy_number": "LoanRefId",
    "client_id": "ClientRefId",  # Not there
    # "json_risk_identifier": "RiskBand",  # risk_identifier
    "sum_insured": "LoanAmount",  # Present
    "policy_term": "LoanTerm",  # Present
    "commencement_date": "DisbursementDate",
    "policy_status": "LoanStatus",
    "payment_method": "PaymentMethod",
    "expiry_date": "CloseDate",
    "province": "Province",
    "approval_date": "ApprovalDate",
    "service_fee": "ServiceFee",
    "interest_rate": "InterestRate",
    "json_client_id": "ClientRefId",
    "loan_schedule": "CLI Sched",
    # "json_total_loan_schedule": "CLI Sched",
    "total_premium": "Monthly CLI Prem",
    # "json_instalment_amount": "Instalment amount",
    "initiation_fee": "Initation Fee Month (incl VAT)",
    # these are for control in policy_client_indlu
    "total_policy_premium_collected": "total_policy_premium_collected"
}
POLICY_CLIENTS_COLUMNS_THF_UPDATE = {
    "loanId": "LoanRefId",
    "total_premium": "CLI Sched",
    "premium": "Monthly CLI Prem",
}
POLICY_SCORE_THF_UPDATE = {
    "id": "id",
    "lapsed": "lapsed",
    # "score": "Application Score",
    # "risk_band": "RiskBand",
}
POLICY_CLIENTS_COLUMNS_CFSA_UPDATE = {
    "policy_number": "Policy Number",
    # "product_id": "product_id",
    # "closed_reason": "closed_reason",
    # "expiry_date": "closed_date",
    # "loan_external_id": "loan_external_id",
}
POLICY_CLIENTS_COLUMNS_CFSA = {
    "policy_number": "Policy Number",
    "client_id": "Client Identifier",  # Not there
    "sum_insured": "Original loan balance",  # Present
    "policy_term": "Term of policy",  # Present
    "commencement_date": "Policy Commencement date",
    "expiry_date": "Policy Expiry Date",
    "sub_scheme": "Sub Scheme Name",
    "json_new_policy_indicator": "New Business Indicator",
    "total_premium": "Prem",
    "premium_frequency": "Premium Frequency",
    # these are for control in policy_client_indlu
    "business_unit": "Division",
    "json_risk_identifier": "Risk Identifier",
    "commission": "Commission",
    "json_binder_fees": "Binder Fee",
    "admin_fee": "GR Admin Fee",
    "json_death_indicator": "Death indicator",
    "json_ptd_indicator": "PTD indicator",
    "json_ttd_indicator": "TTD indicator",
    "json_retrenchment_indicator": "Retrenchment indicator",
    "json_dread_disease_indicator": "Dread disease indicator",
    "json_accidental_indicator": "Accidental death indicator",
    "json_current_loan_balance": "Current outstanding balance",
    "json_installment_amount": "Instalment amount",
    "gender": "Life 1 Gender",
    "primary_id_number": "Life 1 ID",
    "first_name": "Life 1 first name",
    "middle_name": "Life 1 Initials",
    "last_name": "Life 1 Surname",
    "date_of_birth": "Date Of Birth",
    "date_of_death": "Life 1 date of death",
    "address_street": "Life 1 physical address",
    "address_suburb": "Life 1 Physical Address",
    "address_town": "Life 1 Physical Address",
    "postal_code": "Postal Code",
    "phone_number": "Life 1 Telephone",
}
POLICY_CLIENTS_COLUMNS_CFSA_CORRECT = {
    "policy_number": "Policy Number",
    "sum_insured": "Original loan balance",
}
POLICY_CLIENT_COLUMNS_INDLU = {
    "policy_number": "LoanRefId",
    "client_id": "ClientRefId",  # Not there
    "sum_insured": "Loan Amount",  # Present
    "policy_term": "Loan Term",  # Present
    "commencement_date": "Disbursement Date",
    "policy_status": "Status",
    "payment_method": "PaymentMethod",
    "expiry_date": "CloseDate",
    "json_client_id": "ClientRefId",
    "address_province": "Provinsie",
    "json_interest_rate": "Int Rate %",
    "json_approval_date": "Disbursement Date",
    "json_remaining_terms": "Remaining Term",
    "json_total_extracted_installment": "Total extracted installment",
    "json_employer_payment_calendar": "PaymentCalendar\\",
    "json_total_policy_premium_collected": "Total Pd",
    "json_remaining_term": "Remaining Term",
    "json_monthly_fee": "Monthly Fee (incl VAT)",
    "json_total_interest": "Total Interest",
    "json_total_loan_schedule": "CLI Sched",
    "total_premium": "Monthly CLI Prem",
    "sector": "Sector",
    "job_description": "Job Description",
    "gender": "Gender",
    "employer_name": "Employer",
    "primary_id_number": "CIDNum",
    "first_name": "CFirstName",
    "middle_name": "CMidInitial",
    "last_name": "CLastName",
    "date_of_birth": "DOB",
    "address_street": "CResAddressL1",
    "address_suburb": "CResAddressL2",
    "address_town": "CResAddressL4",
    "gross_salary": "GrossSalary",
    "basic_salary": "BasicSalary",
    "phone_number": "CCellPhone",
}

CLIENT_COLUMNS_INDLU = {
    "client_id": "ClientReference",
    "primary_id_number": "IdNumber",
    "first_name": "FirstNames",
    "middle_name": "CMidInitial",
    "last_name": "Surname",
    # "date_of_birth": "DateOfBirth",
    "gender": "Gender",
    # "last_payment_date": "Last Payment Date",
    # "last_payment_month": "Last Payment Month",
    "address_street": "CResAddressL1",
    "address_suburb": "Surburb",
    "address_town": "TownCity",
    "address_province": "Province",
    "postal_code": "Postal Code",
    "gross_salary": "GrossSalary",
    "basic_salary": "BasicSalary",
    "phone_number": "ContactNumber",
    "job_title": "JobTitle",
    "sector": "Sector",
    "employer_name": "Employer",  # end of last
    "date_of_birth": "DOB",
    "province": "CResAddressL2",
    "employment_date": "AddedDate",
    #####

    # "sectors": "Sector",
    # "job_description": "Job Description",
    # "last_payment_date": "Last Payment Date",
    # "last_payment_month": "Last Payment Month",
    # "gender": "Gender",
    # "employer": "Employer",
    # "initials": "CMidInitial",
    # "last_name": "CLastName",
    # "first_name": "CFirstName",
    # "middle_name": "CMidInitial",
    # "primary_id_number": "CIDNum",
    # "date_of_birth": "DOB",
    # # "external_id": "Client Identifier",
    # "address_street": "CResAddressL1",
    # "address_suburb": "CResAddressL2",
    # "address_province": "CResAddressL3",
    # "phone_number": "CCellPhone",
    # "work_phone": "CWorkPhone",
    # "employer_address": "EmployerAddress1",
    # "employer_address_suburb": "EmployerAddress2",
    # "employer_address_province": "EmployerAddress3",
    # "employer_payment_calendar": "PaymentCalendar",
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

DEFAULT_BENEFICIARY_FIELDS = {"beneficiary_gender": "Unknown"}

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

REPAYMENT_COLUMNS_INDLU = {
    "policy_id": "Loan Id",
    "payment_date": "Tran Date",
    "amount": "Nett",
    "branch_name": "Branch Name",
    "client_number": "Client No",
    "loan_payment_method": "Loan Payment Method",
    "ptp_payment_method": "PTP Payment Method",
    "payment_method": "Actual Payment Method",
    "transaction_type": "Tran Type",
    "is_reversed": "Reversed",
    "client_transaction_id": "Client Transaction Id",
    "teller_transaction_number": "Teller Transaction No",
}
REPAYMENT_COLUMNS_MEDIFIN = {
    "policy_id": "Loan ID",
    "payment_date": "Transaction date",
    "amount": "Repayment amount",
}
