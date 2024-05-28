from datetime import date, datetime
from integrations.utils import get_frequency_number


def prepare_life_credit_payload(
        data: list, start_date: date, end_date: date, identifier: str
):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    result = []
    print("Preparing data")
    for policy in data:
        client = policy["client"]
        policy_dependants = policy["policy_dependants"]
        insurer = policy["insurer"]
        spouse = filter(
            lambda x: x if x["relationship"].lower() == "spouse" else None,
            policy_dependants,
        )
        spouse = list(spouse)
        policy_details = policy["policy_details"]

        # constants
        client_identifier = 75
        division_identifier = "0001"
        product_option = "all"
        premium_type = "Regular"
        death_cover_structure = "L"
        ptd_cover_structure = "L"
        retrenchment_cover_structure = "L"
        death_cover_benefit_payment_period = 1
        ptd_cover_benefit_payment_period = 1
        retrenchment_death_payment_period = 30
        death_waiting_period = 3
        ptd_waiting_period = 3
        retrenchment_waiting_period = 6

        policy_details = {
            "TimeStamp": timestamp,
            "ReportPeriodStart": start_date,
            "ReportPeriodEnd": end_date,
            "AdministratorIdentifier": identifier,
            "InsurerName": insurer.get("name", ""),
            "ClientIdentifier": client_identifier,
            "DivisionIdentifier": division_identifier,
            "SubSchemeName": policy["sub_scheme"],
            "PolicyNumber": policy["policy_number"],
            "PricingModelVersion": "",
            "ProductName": policy["product_name"],
            "ProductOption": product_option,
            "PolicyCommencementDate": policy["commencement_date"],
            "PolicyExpiryDate": policy["expiry_date"],
            "TermOfPolicy": policy["policy_term"],
            "PolicyStatus": policy["policy_status"],
            "PolicyStatusDate": timestamp,
            "NewPolicyIndicator": policy_details.get("new_policy_indicator", ""),
            "SalesChannel": policy_details.get("sales_channel", ""),
            "CancelledbyPolicyholderCoolingPeriodInsurer": "",
            "DeathIndicator": policy_details.get("death_indicator", ""),
            "PTDIndicator": policy_details.get("ptd_indicator", ""),
            "IncomeContinuationIndicator": policy_details.get("", ""),
            "DreadDiseaseIndicator": policy_details.get("dread_disease_indicator", ""),
            "RetrenchmentIndicator": policy_details.get("retrenchment_indicator", ""),
            "DeathCoverTermIfDifferenttoPolicyTerm": None,
            "PTDCoverTermIfDifferenttoPolicyTerm": None,
            "IncomeContinuationCoverTermIfDifferenttoPolicyTerm": None,
            "DreadDiseaseCoverTermIfDifferenttoPolicyTerm": None,
            "RetrenchmentCoverTermIfDifferenttoPolicyTerm": None,
            "DeathPremium": policy_details.get("death_premium", ""),
            "PTDPremium": policy_details.get("PTD_premium", ""),
            "IncomeContinuationPremium": 0,
            "DreadDiseasePremium": 0,
            "RetrenchmentPremium": policy_details.get("retrenchment_premium", 0),
            "PremiumFrequency": get_frequency_number(policy["premium_frequency"]),
            "PremiumType": premium_type,
            "DeathOriginalSumAssured": policy_details.get(
                "death_original_sum_assured", 0
            ),
            "PTDOriginalSumAssured": policy_details.get("ptd_current_sum_assured", 0),
            "IncomeContinuationOriginalSumAssured": 0,
            "DreadDiseaseOriginalSumAssured": 0,
            "RetrenchmentOriginalSumAssured": 0,
            "DeathCoverStructure": death_cover_structure,
            "PTDCoverStructure": ptd_cover_structure,
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
            "DeathCurrentSumAssured": policy_details.get(
                "death_current_sum_assured", 0
            ),
            "PTDCurrentSumAssured": policy_details.get("ptd_current_sum_assured", 0),
            "IncomeContinuationCurrentSumAssured": None,
            "DreadDiseaseCurrentSumAssured": None,
            "RetrenchmentCurrentSumAssured": policy_details.get(
                "retrenchment_current_sum_assured", 0
            ),
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
            "TotalPolicyPremiumCollected": policy_details.get(
                "total_policy_premium_collected", 0
            ),
            "TotalPolicyPremiumPayable": policy["total_premium"],
            "TotalPolicyPremiumSubsidy": None,
            "TotalReinsurancePremium": None,
            "TotalReinsurancePremiumPayable": None,
            "TotalFinancialReinsuranceCashflows": None,
            "CommissionFrequency": get_frequency_number(policy["commission_frequency"]),
            "Commission": float(policy["commission_amount"]),
            "AdminBinderFees": policy["admin_fee"],
            "OutsourcingFees": None,
            "MarketingAdvertisingFees": None,
            "ManagementFees": policy_details.get("management_fee", 0),
            "ClaimsHandlingFee": None,
            "TotalGrossClaimAmount": None,
            "GrossClaimPaid": None,
            "ReinsuranceRecoveries": None,
            "OriginalLoanBalance": policy["sum_insured"],
            "CurrentOutstandingBalance": policy_details.get(
                "current_outstanding_balance", 0
            ),
            "InstallmentAmount": policy_details.get("instalment_amount", 0),
            "PrincipalSurname": client.get("last_name", ""),
            "PrincipalFirstName": client.get("first_name", ""),
            "PrincipalInitials": client.get("middle_name", ""),
            "PrincipalID": client.get("primary_id_number", ""),
            "PrincipalGender": client.get("gender", ""),
            "PrincipalDateofBirth": client.get("date_of_birth", ""),
            "PrincipalMemberPhysicalAddress": f"{client['address_street']} {client['address_suburb']} {client['address_town']} {client['address_province']}",
            "PostalCode": client["postal_code"],
            "PrincipalTelephoneNumber": client["phone_number"],
            "PrincipalMemberEmailAddress": client.get("email", ""),
            "IncomeGroup": "",
        }
        # add spouse if they exists
        # split full name it first name middlename and last name
        if spouse:  # Check if spouse list is not empty
            full_name = spouse[0]["dependant_name"]
            full_name = full_name.split(" ")
            if len(full_name) == 1:
                policy_details["SpouseName"] = full_name[0]
                policy_details["SpouseMiddleName"] = ""
                policy_details["SpouseLastName"] = ""
            elif len(full_name) == 2:
                policy_details["SpouseName"] = full_name[0]
                policy_details["SpouseMiddleName"] = ""
                policy_details["SpouseLastName"] = full_name[1]
            elif len(full_name) == 3:
                policy_details["SpouseName"] = full_name[0]
                policy_details["SpouseMiddleName"] = full_name[1]
                policy_details["SpouseLastName"] = full_name[2]
            else:
                policy_details["SpouseName"] = full_name[0]
                policy_details["SpouseMiddleName"] = " ".join(full_name[1:-1])
                policy_details["SpouseLastName"] = full_name[-1]

            spouse = spouse[0]
            policy_details["SpouseID"] = spouse["primary_id_number"]
            policy_details["SpouseGender"] = spouse["dependant_gender"]
            policy_details["SpouseDateofBirth"] = spouse["dependant_dob"]
            policy_details["SpouseIndicator"] = True
        else:
            # Set default values to "n/a"
            policy_details["SpouseName"] = "n/a"
            policy_details["SpouseMiddleName"] = "n/a"
            policy_details["SpouseLastName"] = "n/a"
            policy_details["SpouseID"] = "n/a"
            policy_details["SpouseGender"] = "n/a"
            policy_details["SpouseDateofBirth"] = "n/a"
            policy_details["SpouseIndicator"] = False

        # policy_details["SpouseCoverAmount"] = spouse["cover_amount"]
        # policy_details["SpouseCoverCommencementDate"] = spouse[
        #     "cover_commencement_date"
        # ]
        result.append(policy_details)

    return result
