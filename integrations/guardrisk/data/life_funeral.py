from datetime import date, datetime
from integrations.utils import getFrequencyNumber


def prepare_life_funeral_payload(data: list, start_date: date, end_date: date):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    result = []
    for policy in data:
        insurer = policy["insurer"]
        client = policy["client"]
        policy_beneficiary = policy["policy_beneficiary"]
        no_of_dependencies = len(policy["policy_dependants"])
        # get spouse from dependants using relationship
        spouse = (
            lambda x: x if x["relationship"].lower() == "spouse" else None,
            policy["policy_dependants"],
        )
        spouse = list(spouse)
        other_dependants = filter(
            lambda x: x if x["relationship"].lower() != "spouse" else None,
            policy["policy_dependants"],
        )
        other_dependants = list(other_dependants)

        insurer = policy["insurer"]

        policy_details = {
            "TimeStamp": timestamp,
            "ReportPeriodStart": start_date,
            "ReportPeriodEnd": end_date,
            "AdministratorIdentifier": "Getsure",
            "InsurerName": insurer.get("name", ""),
            "ClientIdentifier": "143",
            "DivisionIdentifier": "1",
            "SubSchemeName": "Getsure (Pty) Ltd",
            "PolicyNumber": policy["policy_number"],
            "ProductName": policy["product_name"],
            "ProductOption": "N/A",
            "PolicyCommencementDate": policy["commencement_date"],
            "PolicyExpiryDate": policy["expiry_date"],
            "TermofPolicy": policy["policy_term"],
            "PolicyStatus": policy["policy_status"],
            "PolicyStatusDate": policy["updated"],
            "NewPolicyIndicator": "P",
            "SalesChannel": "Voice Only",
            "CancelledbyPolicyholderCoolingPeriodInsurer": "",
            "DeathIndicator": "Y",
            "PTDIndicator": "Y",
            "IncomeContinuationIndicator": "N",
            "PremiumFrequency": getFrequencyNumber(policy["premium_frequency"]),
            "PremiumType": "Regular",
            "DeathOriginalSumAssured": policy["sum_insured"],
            "PTDOriginalSumAssured": policy["sum_insured"],
            "DeathCoverStructure": "Lump Sum",
            "DeathCurrentSumAssured": policy["sum_insured"],
            "PTDCoverStructure": "Combined",
            "ReinsurerName": "N/A",
            "DeathCurrentRISumAssured": "N/A",
            "DeathRIPremium": "N/A",
            "DeathRIPercentage": "N/A",
            "TotalPolicyPremiumCollected": "sample text 29",
            "TotalPolicyPremiumPayable": "sample text 30",
            "TotalPolicyPremium": policy["total_premium_total"],
            "TotalPolicyPremiumSubsidy": policy["total_premium_total"],
            "TotalReinsurancePremium": policy["total_premium_total"],
            "TotalReinsurancePremiumPayable": policy["total_premium_total"],
            "TotalFinancialReinsuranceCashflows": policy["total_premium_total"],
            "TotalFinancialReinsurancePayable": policy["total_premium_total"],
            "CommissionFrequency": getFrequencyNumber(policy["commission_frequency"]),
            "Commission": policy["commission_amount"],
            "AdminBinderFees": "0.00",
            "OutsourcingFees": "0.00",
            "MarketingAdvertisingFees": "0.00",
            "ManagementFees": "0.00",
            "ClaimsHandlingFee": "0.00",
            "TotalGrossClaimAmount": "0.00",
            "GrossClaimPaid": "0.00",
            "ReinsuranceRecoveries": "0.00",
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
            "SpouseIndicator": "N",
            "NumberofAdultDependents": "0",
            "NumberofChildDependents": "0",
            "NumberofExtendedFamily": "0",
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
            # policy_details["SpouseCoverAmount"] = spouse["cover_amount"]
            # policy_details["SpouseCoverCommencementDate"] = spouse[
            #     "cover_commencement_date"
            # ]

        # add dependants of they exists
        for dependant in other_dependants:
            # split full name it first name middlename and last name
            full_name = dependant["dependant_name"]
            full_name = full_name.split(" ")
            if len(full_name) == 1:
                policy_details[f"Dependent{
                    dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = ""
                policy_details[f"Dependent{dependant['index']}Surname"] = ""
            elif len(full_name) == 2:
                policy_details[f"Dependent{
                    dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = ""
                policy_details[f"Dependent{
                    dependant['index']}Surname"] = full_name[1]
            elif len(full_name) == 3:
                policy_details[f"Dependent{
                    dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{
                    dependant['index']}Initials"] = full_name[1]
                policy_details[f"Dependent{
                    dependant['index']}Surname"] = full_name[2]
            else:
                policy_details[f"Dependent{
                    dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = " ".join(
                    full_name[1:-1]
                )
                policy_details[f"Dependent{
                    dependant['index']}Surname"] = full_name[-1]

            policy_details[f"Dependent{dependant['index']}ID"] = dependant[
                "primary_id_number"
            ]
            policy_details[f"Dependent{dependant['index']}Gender"] = dependant[
                "dependant_gender"
            ]
            policy_details[f"Dependent{dependant['index']}DateofBirth"] = dependant[
                "dependant_dob"
            ]
            # policy_details[f"Dependent{dependant['index']}Type"] = dependant["type"]
            # policy_details[f"Dependent{dependant['index']}CoverAmount"] = dependant[
            #     "cover_amount"
            # ]
            # policy_details[f"Dependent{dependant['index']}CoverCommencementDate"] = (
            #     dependant["cover_commencement_date"]
            # )

        result.append(policy_details)

    return result
