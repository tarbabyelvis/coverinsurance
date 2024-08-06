import json
from datetime import date, datetime

from config.models import Relationships
from integrations.utils import get_frequency_number, populate_dependencies, is_new_policy


def prepare_life_credit_payload(
        data: list, start_date: date, end_date: date, client_identifier
):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    relationships = Relationships.objects.all()
    result = []
    print("Preparing credit life data")
    for policy in data:
        client = policy["client"]
        policy_dependants = policy["policy_dependants"]
        insurer = policy["insurer"]
        spouse = filter(
            lambda x: x if relationships[x["relationship"]].name.lower() == "spouse" else None,
            policy_dependants,
        )
        spouse = list(spouse)
        other_dependants_filter = filter(
            lambda x: x if relationships[x["relationship"]].lower() != "spouse" else None,
            policy_dependants,
        )
        other_dependants = list(other_dependants_filter)
        try:
            if isinstance(policy["policy_details"], dict):
                policy_details = policy["policy_details"]
            else:
                policy_details = json.loads(policy["policy_details"])
        except json.JSONDecodeError as e:
            policy_details = policy["policy_details"]
            print(f"failed to parse json but read it now...")

        # constants
        product_option = "all"
        premium_type = "Regular"
        death_cover_structure = "L"
        retrenchment_cover_structure = "L"
        death_cover_benefit_payment_period = 1
        ptd_cover_benefit_payment_period = 1
        retrenchment_death_payment_period = 30
        death_waiting_period = 3
        ptd_waiting_period = 3
        retrenchment_waiting_period = 6
        current_loan_balance = policy["policy_details"]["current_outstanding_balance"]
        policy_number = policy["policy_number"]
        division = policy["business_unit"]
        premium = policy["premium"]
        details = {
            "TimeStamp": timestamp,
            "ReportPeriodStart": start_date,
            "ReportPeriodEnd": end_date,
            "AdministratorIdentifier": policy["entity"],
            "InsurerName": insurer["name"],
            "ClientIdentifier": client_identifier,
            "DivisionIdentifier": division,
            "SubSchemeName": policy["sub_scheme"],
            "PolicyNumber": policy_number,
            "PricingModelVersion": "",
            "ProductName": policy["product_name"],
            "ProductOption": product_option,
            "PolicyCommencementDate": policy["commencement_date"],
            "PolicyExpiryDate": policy.get("expiry_date", ""),
            "TermOfPolicy": policy["policy_term"],
            "PolicyStatus": policy["policy_status"],
            "PolicyStatusDate": timestamp,
            "NewPolicyIndicator": is_new_policy(policy["commencement_date"], start_date, end_date),
            "SalesChannel": policy_details.get("sales_channel", ""),
            "CancelledbyPolicyholderCoolingPeriodInsurer": "",
            "DeathIndicator": "Y",
            "PTDIndicator": "Y",
            "IncomeContinuationIndicator": "N",
            "DreadDiseaseIndicator": "N",
            "RetrenchmentIndicator": "Y",
            "DeathCoverTermIfDifferenttoPolicyTerm": None,
            "PTDCoverTermIfDifferenttoPolicyTerm": None,
            "IncomeContinuationCoverTermIfDifferenttoPolicyTerm": None,
            "DreadDiseaseCoverTermIfDifferenttoPolicyTerm": None,
            "RetrenchmentCoverTermIfDifferenttoPolicyTerm": None,
            "DeathPremium": premium,
            "PTDPremium": premium,
            "IncomeContinuationPremium": 0,
            "DreadDiseasePremium": 0,
            "RetrenchmentPremium": premium,
            "PremiumFrequency": get_frequency_number(policy.get("premium_frequency")),
            "PremiumType": premium_type,
            "DeathOriginalSumAssured": policy.get("sum_insured"),
            "PTDOriginalSumAssured": policy.get("sum_insured"),
            "IncomeContinuationOriginalSumAssured": policy.get("sum_insured"),
            "DreadDiseaseOriginalSumAssured": policy.get("sum_insured"),
            "RetrenchmentOriginalSumAssured": policy.get("sum_insured"),
            "DeathCoverStructure": death_cover_structure,
            "PTDCoverStructure": policy_details.get("death_cover_structure", "L"),
            "IncomeContinuationCoverStructure": None,
            "DreadDiseaseCoverStructure": None,
            "RetrenchmentCoverStructure": retrenchment_cover_structure,
            "DeathCoverBenefitPaymentPeriod": death_cover_benefit_payment_period,
            "PTDCoverBenefitPaymentPeriod": ptd_cover_benefit_payment_period,
            "IncomeContinuationCoverBenefitPaymentPeriod": None,
            "DreadDiseaseCoverBenefitPaymentPeriod": None,
            "RetrenchmentCoverBenefitPaymentPeriod": retrenchment_death_payment_period,
            "DeathCoverWaitingPeriod": death_waiting_period,
            "PTDCoverWaitingPeriod": ptd_waiting_period,
            "IncomeContinuationCoverWaitingPeriod": None,
            "PHICoverWaitingPeriod": None,
            "RetrenchmentCoverWaitingPeriod": retrenchment_waiting_period,
            "DeathCurrentSumAssured": current_loan_balance,
            "PTDCurrentSumAssured": current_loan_balance,
            "IncomeContinuationCurrentSumAssured": None,
            "DreadDiseaseCurrentSumAssured": None,
            "RetrenchmentCurrentSumAssured": current_loan_balance,
            "ReinsurerName": None,
            "DeathCurrentRISumAssured": None,
            "PTDCurrentRISumAssured": None,
            "IncomeContinuationCurrentRISumAssured": None,
            "DreadDiseaseCurrentRISumAssured": None,
            "RetrenchmentCurrentRISumAssured": None,
            "DeathRIPremium": None,
            "PTDRIPremium": None,
            "IncomeContinuationRIPremium": None,
            "DreadDiseaseRIPremium": None,
            "RetrenchmentRIPremium": None,
            "DeathRIPercentage": None,
            "PTDRIPercentage": None,
            "IncomeContinuationRIPercentage": None,
            "DreadDiseaseRIPercentage": None,
            "RetrenchmentRIPercentage": None,
            "TotalPolicyPremiumCollected": policy_details.get("total_policy_premium_collected", "0.00"),
            "TotalPolicyPremiumPayable": policy_details.get("total_loan_schedule", "0.00"),
            "TotalPolicyPremiumSubsidy": None,
            "TotalReinsurancePremium": None,
            "TotalReinsurancePremiumPayable": None,
            "TotalFinancialReinsuranceCashflows": None,
            "CommissionFrequency": get_frequency_number(policy.get("commission_frequency", "")),
            "Commission": float(policy["commission_amount"]),
            "AdminBinderFees": policy["policy_details"].get("binder_fees", ""),
            "OutsourcingFees": None,
            "MarketingAdvertisingFees": None,
            "ManagementFees": policy.get("admin_fee", ""),
            "ClaimsHandlingFee": None,
            "TotalGrossClaimAmount": None,
            "GrossClaimPaid": None,
            "ReinsuranceRecoveries": None,
            "OriginalLoanBalance": policy["sum_insured"],
            "CurrentOutstandingBalance": current_loan_balance,
            "InstallmentAmount": policy_details.get("installment_amount", 0),
            "PrincipalSurname": client.get("last_name", ""),
            "PrincipalFirstName": client.get("first_name", ""),
            "PrincipalInitials": client.get("middle_name", ""),
            "PrincipalID": client.get("primary_id_number", ""),
            "PrincipalGender": client.get("gender", ""),
            "PrincipalDateofBirth": client.get("date_of_birth", ""),
            "PrincipalMemberPhysicalAddress": f"{client['address_street']} {client['address_suburb']} "
                                              f"{client['address_town']} {client['address_province']}",
            "PostalCode": client["postal_code"],
            "PrincipalTelephoneNumber": client["phone_number"],
            "PrincipalMemberEmailAddress": client.get("email", ""),
            "IncomeGroup": policy_details.get("income_group", ""),
        }
        # add spouse if they exists
        # split full name it first name middlename and last name
        if spouse:  # Check if spouse list is not empty
            # print(f'spouses {spouse}')
            full_name = spouse[0]["dependant_name"]
            if full_name:
                full_name = full_name.split(" ")
                if len(full_name) == 1:
                    if len(full_name) == 1:
                        details["SpouseFirstName"] = full_name[0]
                        details["SpouseMiddleName"] = ""
                        details["SpouseSurname"] = ""
                        details["SpouseInitials"] = full_name[0][0]
                elif len(full_name) == 2:
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = ""
                    details["SpouseSurname"] = full_name[1]
                    details["SpouseInitials"] = f"{full_name[0][0]} {full_name[1][0]}"
                elif len(full_name) == 3:
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = full_name[1]
                    details["SpouseSurname"] = full_name[2]
                    details["SpouseInitials"] = f"{full_name[0][0]} {full_name[1][0]} {full_name[2][0]}"
                else:
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = " ".join(full_name[1:-1])
                    details["SpouseSurname"] = full_name[-1]
                    details["SpouseInitials"] = f" {full_name[0][0]} {full_name[1][0]} {full_name[-1][0]}"

            spouse = spouse[0]
            details["SpouseID"] = spouse.get("primary_id_number", "")
            details["SpouseGender"] = spouse.get("dependant_gender")
            details["SpouseDateofBirth"] = spouse.get("dependant_dob")
            details["SpouseCoverAmount"] = spouse.get("cover_amount", "0.00")
            details["SpouseCoverCommencementDate"] = policy["commencement_date"]
            details["SpouseIndicator"] = 'Y'
        else:
            details["SpouseFirstName"] = ""
            details["SpouseMiddleName"] = ""
            details["SpouseSurname"] = ""
            details["SpouseID"] = ""
            details["SpouseGender"] = ""
            details["SpouseDateofBirth"] = ""
            details["SpouseCoverAmount"] = ""
            details["SpouseInitials"] = ""
            details["SpouseIndicator"] = 'N'

        populate_dependencies(other_dependants, details)

        result.append(details)

    return result
