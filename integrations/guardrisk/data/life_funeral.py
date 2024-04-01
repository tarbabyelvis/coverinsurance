from datetime import date, datetime


def prepare_life_funeral_payload(data: list, start_date: date, end_date: date):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")
    insurer = policy["insurer"]

    result = []
    for policy in data:
        client = policy["client"]
        policy_beneficiary = policy["policy_beneficiary"]
        # get spouse from dependants using relationship
        spouse = filter(
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
            "AdministratorIdentifier": "sample text 4",
            "InsurerName": insurer.get("name", ""),
            "ClientIdentifier": "00123",
            "DivisionIdentifier": "sample text 6",
            "SubSchemeName": "sample text 7",
            "PolicyNumber": policy["policy_term"],
            "ProductName": policy["product_name"],
            "ProductOption": "sample text 10",
            "PolicyCommencementDate": "sample text 11",
            "PolicyExpiryDate": policy["expiry_date"],
            "TermofPolicy": policy["policy_term"],
            "PolicyStatus": policy["policy_status"],
            "PolicyStatusDate": "sample text 15",
            "NewPolicyIndicator": "sample text 16",
            "SalesChannel": "sample text 17",
            "CancelledbyPolicyholderCoolingPeriodInsurer": "sample text 18",
            "DeathIndicator": "sample text 19",
            "PremiumFrequency": "sample text 20",
            "PremiumType": "sample text 21",
            "DeathOriginalSumAssured": "sample text 22",
            "DeathCoverStructure": "sample text 23",
            "DeathCurrentSumAssured": "sample text 24",
            "ReinsurerName": "sample text 25",
            "DeathCurrentRISumAssured": "sample text 26",
            "DeathRIPremium": "sample text 27",
            "DeathRIPercentage": "sample text 28",
            "TotalPolicyPremiumCollected": "sample text 29",
            "TotalPolicyPremiumPayable": "sample text 30",
            "TotalPolicyPremium": "sample text 31",
            "TotalPolicyPremiumSubsidy": "sample text 32",
            "TotalReinsurancePremium": "sample text 33",
            "TotalReinsurancePremiumPayable": "sample text 34",
            "TotalFinancialReinsuranceCashflows": "sample text 35",
            "TotalFinancialReinsurancePayable": "sample text 36",
            "CommissionFrequency": "sample text 37",
            "Commission": "sample text 38",
            "AdminBinderFees": "sample text 39",
            "OutsourcingFees": "sample text 40",
            "MarketingAdvertisingFees": "sample text 41",
            "ManagementFees": "sample text 42",
            "ClaimsHandlingFee": "sample text 43",
            "TotalGrossClaimAmount": "sample text 44",
            "GrossClaimPaid": "sample text 45",
            "ReinsuranceRecoveries": "sample text 46",
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
            "IncomeGroup": "sample text 57",
            "SpouseIndicator": "sample text 58",
            "NumberofAdultDependents": "sample text 59",
            "NumberofChildDependents": "sample text 60",
            "NumberofExtendedFamily": "sample text 61",
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
                policy_details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = ""
                policy_details[f"Dependent{dependant['index']}Surname"] = ""
            elif len(full_name) == 2:
                policy_details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = ""
                policy_details[f"Dependent{dependant['index']}Surname"] = full_name[1]
            elif len(full_name) == 3:
                policy_details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = full_name[1]
                policy_details[f"Dependent{dependant['index']}Surname"] = full_name[2]
            else:
                policy_details[f"Dependent{dependant['index']}FirstName"] = full_name[0]
                policy_details[f"Dependent{dependant['index']}Initials"] = " ".join(
                    full_name[1:-1]
                )
                policy_details[f"Dependent{dependant['index']}Surname"] = full_name[-1]

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
