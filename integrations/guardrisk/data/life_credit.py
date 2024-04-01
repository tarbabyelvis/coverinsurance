from datetime import date, datetime


def prepare_life_credit_payload(data: list, start_date: date, end_date: date):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    result = []
    for policy in data:
        client = policy["client"]
        policy_dependants = policy["policy_dependants"]
        insurer = policy["insurer"]
        spouse = filter(
            lambda x: x if x["relationship"].lower() == "spouse" else None,
            policy_dependants,
        )
        spouse = list(spouse)

        policy_details = {
            "TimeStamp": timestamp,
            "ReportPeriodStart": start_date,
            "ReportPeriodEnd": end_date,
            "AdministratorIdentifier": "",
            "InsurerName": insurer.get("name", ""),
            "ClientIdentifier": client["primary_id_number"],
            "DivisionIdentifier": "0001",
            "SubSchemeName": policy["sub_scheme"],
            "PolicyNumber": policy["policy_number"],
            "PricingModelVersion": "",
            "ProductName": policy["product_name"],
            "ProductOption": "",
            "PolicyCommencementDate": policy["commencement_date"],
            "PolicyExpiryDate": policy["expiry_date"],
            "TermOfPolicy": policy["policy_term"],
            "PolicyStatus": policy["policy_status"],
            "PolicyStatusDate": timestamp,
            "NewPolicyIndicator": "",
            "SalesChannel": "",
            "CancelledbyPolicyholderCoolingPeriodInsurer": "",
            "DeathIndicator": "",
            "PTDIndicator": "",
            "IncomeContinuationIndicator": "",
            "DreadDiseaseIndicator": "",
            "RetrenchmentIndicator": "",
            "DeathCoverTermIfDifferenttoPolicyTerm": "",
            "PTDCoverTermIfDifferenttoPolicyTerm": "",
            "IncomeContinuationCoverTermIfDifferenttoPolicyTerm": "",
            "DreadDiseaseCoverTermIfDifferenttoPolicyTerm": "",
            "RetrenchmentCoverTermIfDifferenttoPolicyTerm": "",
            "DeathPremium": "",
            "PTDPremium": "",
            "IncomeContinuationPremium": "",
            "DreadDiseasePremium": "",
            "RetrenchmentPremium": "",
            "PremiumFrequency": "",
            "PremiumType": "",
            "DeathOriginalSumAssured": "",
            "PTDOriginalSumAssured": "",
            "IncomeContinuationOriginalSumAssured": "",
            "DreadDiseaseOriginalSumAssured": "",
            "RetrenchmentOriginalSumAssured": "",
            "DeathCoverStructure": "",
            "PTDCoverStructure": "",
            "IncomeContinuationCoverStructure": "",
            "DreadDiseaseCoverStructure": "",
            "RetrenchmentCoverStructure": "",
            "DeathCoverBenefitPaymentPeriod": "",
            "PTDCoverBenefitPaymentPeriod": "",
            "IncomeContinuationCoverBenefitPaymentPeriod": "",
            "DreadDiseaseCoverBenefitPaymentPeriod": "",
            "RetrenchmentCoverBenefitPaymentPeriod": "",
            "DeathCoverWaitingPeriod": "",
            "PTDCoverWaitingPeriod": "",
            "IncomeContinuationCoverWaitingPeriod": "",
            "PHICoverWaitingPeriod": "",
            "RetrenchmentCoverWaitingPeriod": "",
            "DeathCurrentSumAssured": "",
            "PTDCurrentSumAssured": "",
            "IncomeContinuationCurrentSumAssured": "",
            "DreadDiseaseCurrentSumAssured": "",
            "RetrenchmentCurrentSumAssured": "",
            "ReinsurerName": "",
            "DeathCurrentRISumAssured": "",
            "PTDCurrentRISumAssured": "",
            "IncomeContinuationCurrentRISumAssured": "",
            "DreadDiseaseCurrentRISumAssured": "",
            "RetrenchmentCurrentRISumAssured": "",
            "DeathRIPremium": "",
            "PTDRIPremium": "",
            "IncomeContinuationRIPremium": "",
            "DreadDiseaseRIPremium": "",
            "RetrenchmentRIPremium": "",
            "DeathRIPercentage": "",
            "PTDRIPercentage": "",
            "IncomeContinuationRIPercentage": "",
            "DreadDiseaseRIPercentage": "",
            "RetrenchmentRIPercentage": "",
            "TotalPolicyPremiumCollected": "",
            "TotalPolicyPremiumPayable": "",
            "TotalPolicyPremiumSubsidy": "",
            "TotalReinsurancePremium": "",
            "TotalReinsurancePremiumPayable": "",
            "TotalFinancialReinsuranceCashflows": "",
            "CommissionFrequency": policy["commission_frequency"],
            "Commission": float(policy["commission_amount"]),
            "AdminBinderFees": policy["admin_fee"],
            "OutsourcingFees": "",
            "MarketingAdvertisingFees": "",
            "ManagementFees": "",
            "ClaimsHandlingFee": "",
            "TotalGrossClaimAmount": "",
            "GrossClaimPaid": "",
            "ReinsuranceRecoveries": "",
            "OriginalLoanBalance": "",
            "CurrentOutstandingBalance": "",
            "InstallmentAmount": "",
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
        if spouse:
            # split full name it first name middlename and last name
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
            # policy_details["SpouseCoverAmount"] = spouse["cover_amount"]
            # policy_details["SpouseCoverCommencementDate"] = spouse[
            #     "cover_commencement_date"
            # ]
        result.append(policy_details)

    return result
