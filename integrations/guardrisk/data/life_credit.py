from datetime import date, datetime


def prepare_life_credit_payload(data: list, start_date: date, end_date: date):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    result = []
    for policy in data:
        client = policy["client"]
        policy_beneficiary = policy["policy_beneficiary"]
        policy_dependants = policy["policy_dependants"]
        insurer = policy["insurer"]

        # spouse = {
        #     key: value
        #     for key, value in data.items()
        #     if key == "relationship" and value == "FK"
        # }
        print(policy_beneficiary)
        print(type(policy_beneficiary))

        result.append(
            {
                "TimeStamp": timestamp,
                "ReportPeriodStart": start_date,
                "ReportPeriodEnd": end_date,
                "AdministratorIdentifier": "sample text 4",
                "InsurerName": insurer.get("name", ""),
                "ClientIdentifier": client["primary_id_number"],
                "DivisionIdentifier": "0001",
                "SubSchemeName": policy["sub_scheme"],
                "PolicyNumber": policy["policy_number"],
                "PricingModelVersion": "sample text 8",
                "ProductName": policy["product_name"],
                "ProductOption": "sample text 10",
                "PolicyCommencementDate": policy["commencement_date"],
                "PolicyExpiryDate": policy["expiry_date"],
                "TermOfPolicy": policy["policy_term"],
                "PolicyStatus": policy["policy_status"],
                "PolicyStatusDate": timestamp,
                "NewPolicyIndicator": "sample text 16",
                "SalesChannel": "sample text 17",
                "CancelledbyPolicyholderCoolingPeriodInsurer": "sample text 18",
                "DeathIndicator": "sample text 19",
                "PTDIndicator": "sample text 20",
                "IncomeContinuationIndicator": "sample text 21",
                "DreadDiseaseIndicator": "sample text 22",
                "RetrenchmentIndicator": "sample text 23",
                "DeathCoverTermIfDifferenttoPolicyTerm": "sample text 24",
                "PTDCoverTermIfDifferenttoPolicyTerm": "sample text 25",
                "IncomeContinuationCoverTermIfDifferenttoPolicyTerm": "sample text 26",
                "DreadDiseaseCoverTermIfDifferenttoPolicyTerm": "sample text 27",
                "RetrenchmentCoverTermIfDifferenttoPolicyTerm": "sample text 28",
                "DeathPremium": "sample text 29",
                "PTDPremium": "sample text 30",
                "IncomeContinuationPremium": "sample text 31",
                "DreadDiseasePremium": "sample text 32",
                "RetrenchmentPremium": "sample text 33",
                "PremiumFrequency": "sample text 34",
                "PremiumType": "sample text 35",
                "DeathOriginalSumAssured": "sample text 36",
                "PTDOriginalSumAssured": "sample text 37",
                "IncomeContinuationOriginalSumAssured": "sample text 38",
                "DreadDiseaseOriginalSumAssured": "sample text 39",
                "RetrenchmentOriginalSumAssured": "sample text 40",
                "DeathCoverStructure": "sample text 41",
                "PTDCoverStructure": "sample text 42",
                "IncomeContinuationCoverStructure": "sample text 43",
                "DreadDiseaseCoverStructure": "sample text 44",
                "RetrenchmentCoverStructure": "sample text 45",
                "DeathCoverBenefitPaymentPeriod": "sample text 46",
                "PTDCoverBenefitPaymentPeriod": "sample text 47",
                "IncomeContinuationCoverBenefitPaymentPeriod": "sample text 48",
                "DreadDiseaseCoverBenefitPaymentPeriod": "sample text 49",
                "RetrenchmentCoverBenefitPaymentPeriod": "sample text 50",
                "DeathCoverWaitingPeriod": "sample text 51",
                "PTDCoverWaitingPeriod": "sample text 52",
                "IncomeContinuationCoverWaitingPeriod": "sample text 53",
                "PHICoverWaitingPeriod": "sample text 54",
                "RetrenchmentCoverWaitingPeriod": "sample text 55",
                "DeathCurrentSumAssured": "sample text 56",
                "PTDCurrentSumAssured": "sample text 57",
                "IncomeContinuationCurrentSumAssured": "sample text 58",
                "DreadDiseaseCurrentSumAssured": "sample text 59",
                "RetrenchmentCurrentSumAssured": "sample text 60",
                "ReinsurerName": "sample text 61",
                "DeathCurrentRISumAssured": "sample text 62",
                "PTDCurrentRISumAssured": "sample text 63",
                "IncomeContinuationCurrentRISumAssured": "sample text 64",
                "DreadDiseaseCurrentRISumAssured": "sample text 65",
                "RetrenchmentCurrentRISumAssured": "sample text 66",
                "DeathRIPremium": "sample text 67",
                "PTDRIPremium": "sample text 68",
                "IncomeContinuationRIPremium": "sample text 69",
                "DreadDiseaseRIPremium": "sample text 70",
                "RetrenchmentRIPremium": "sample text 71",
                "DeathRIPercentage": "sample text 72",
                "PTDRIPercentage": "sample text 73",
                "IncomeContinuationRIPercentage": "sample text 74",
                "DreadDiseaseRIPercentage": "sample text 75",
                "RetrenchmentRIPercentage": "sample text 76",
                "TotalPolicyPremiumCollected": "sample text 77",
                "TotalPolicyPremiumPayable": "sample text 78",
                "TotalPolicyPremiumSubsidy": "sample text 79",
                "TotalReinsurancePremium": "sample text 80",
                "TotalReinsurancePremiumPayable": "sample text 81",
                "TotalFinancialReinsuranceCashflows": "sample text 82",
                "CommissionFrequency": policy["commission_frequency"],
                "Commission": float(policy["commission_amount"]),
                "AdminBinderFees": policy["admin_fee"],
                "OutsourcingFees": "sample text 86",
                "MarketingAdvertisingFees": "sample text 87",
                "ManagementFees": "sample text 88",
                "ClaimsHandlingFee": "sample text 89",
                "TotalGrossClaimAmount": "sample text 90",
                "GrossClaimPaid": "sample text 91",
                "ReinsuranceRecoveries": "sample text 92",
                "OriginalLoanBalance": "sample text 93",
                "CurrentOutstandingBalance": "sample text 94",
                "InstallmentAmount": "sample text 95",
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
                "IncomeGroup": "sample text 106",
                "SpouseIndicator": "sample text 107",
                "SpouseSurname": client.get("last_name", ""),
                "SpouseFirstName": client.get("first_name", ""),
                "SpouseInitials": client.get("middle_name", ""),
                "SpouseID": "sample text 111",
                "SpouseGender": client.get("gender", ""),
                "SpouseDateofBirth": client.get("date_of_birth", ""),
                "SpouseCoverAmount": "sample text 114",
            }
        )

    return result
