import json
from datetime import date, datetime

from config.models import Relationships
from core.utils import get_initial_letter
from integrations.utils import get_frequency_number

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


def prepare_life_funeral_payload(data: list, start_date: date, end_date: date):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    result = []
    relationships = Relationships.objects.all()
    print("Preparing funeral data...")
    for policy in data:
        try:
            print(f'policy id being loaded {policy["id"]}')
            policy_details = json.loads(policy["policy_details"])
            print(f'policy details successful:: {policy_details}')
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data: {e}")
        else:
            insurer = policy["insurer"]
            client = policy["client"]
            policy_beneficiary = policy["policy_beneficiary"]
            no_of_dependencies = len(policy["policy_dependants"])
            # get spouse from dependants using relationship
            spouse = (
                lambda x: x if relationships[x["relationship"]].lower() == "spouse" else None,
                policy["policy_dependants"],
            )
            spouse = list(spouse)
            other_dependants = filter(
                lambda x: x if relationships[x["relationship"]].lower() != "spouse" else None,
                policy["policy_dependants"],
            )
            other_dependants = list(other_dependants)
            number_of_dependencies = len(spouse) + len(other_dependants)
            insurer = policy["insurer"]
            details = {
                "TimeStamp": timestamp,
                "ReportPeriodStart": start_date,
                "ReportPeriodEnd": end_date,
                "AdministratorIdentifier": "Getsure",
                "InsurerName": insurer.get("name", ""),
                "ClientIdentifier": "143",
                "DivisionIdentifier": "1",
                "SubSchemeName": "Getsure (Pty) Ltd",
                "PolicyNumber": policy.get("policy_number", ""),
                "ProductName": policy.get("product_name"),
                "ProductOption": product_option,
                "PolicyCommencementDate": policy["commencement_date"],
                "PolicyExpiryDate": policy.get("expiry_date", ""),
                "TermofPolicy": policy["policy_term"],
                "PolicyStatus": policy["policy_status"],
                "PolicyStatusDate": policy_details.get("policy_status_date", ""),
                "NewPolicyIndicator": policy_details.get("new_policy_indicator", "P"),
                "SalesChannel": policy_details.get("sales_channel", "Direct marketing via internet"),
                "CancelledbyPolicyholderCoolingPeriodInsurer": "",
                "DeathIndicator": policy_details.get("death_indicator", "Y"),
                "PTDIndicator": "Y",
                "IncomeContinuationIndicator": "N",
                "PremiumFrequency": get_frequency_number(policy.get("premium_frequency", "12")),
                "PremiumType": premium_type,
                "DeathOriginalSumAssured": policy.get("death_original_sum_assured", ""),
                "PTDOriginalSumAssured": policy_details.get("ptd_original_sum_insured", ""),
                "DeathCoverStructure": policy_details.get("death_cover_structure", "Lump sum"),
                "DeathCurrentSumAssured": policy_details.get("death_current_sum_insured", ""),
                "PTDCoverStructure": "Combined",
                "ReinsurerName": "N/A",
                "DeathCurrentRISumAssured": "N/A",
                "DeathRIPremium": "N/A",
                "DeathRIPercentage": "N/A",
                "TotalPolicyPremiumCollected": policy["total_premium"],
                "TotalPolicyPremiumPayable": policy["total_premium"],  # TODO subtract total premium from sum_insured
                "TotalPolicyPremium": policy["total_premium"],
                "TotalPolicyPremiumSubsidy": policy["total_premium"],
                "TotalReinsurancePremium": policy["total_premium"],
                "TotalReinsurancePremiumPayable": policy["total_premium"],
                "TotalFinancialReinsuranceCashflows": policy["total_premium"],
                "TotalFinancialReinsurancePayable": policy["total_premium"],
                "CommissionFrequency": get_frequency_number(policy["commission_frequency"]),
                "Commission": policy["commission_amount"],
                "AdminBinderFees": policy["admin_fee"],
                "OutsourcingFees": None,
                "MarketingAdvertisingFees": None,
                "ManagementFees": policy_details.get("management_fee", ""),
                "ClaimsHandlingFee": None,
                "TotalGrossClaimAmount": None,
                "GrossClaimPaid": None,
                "ReinsuranceRecoveries": None,
                "PrincipalSurname": client.get("last_name", ""),
                "PrincipalFirstName": client.get("first_name", ""),
                "PrincipalInitials": f"{get_initial_letter(client.get("first_name", ""))} {get_initial_letter(client.get("middle_name", ""))} {get_initial_letter(client.get("last_name", ""))}",
                "PrincipalID": client.get("primary_id_number", ""),
                "PrincipalGender": client.get("gender", "U"),
                "PrincipalDateofBirth": client.get("date_of_birth", ""),
                "PrincipalMemberPhysicalAddress": f"{client.get('address_street', '')} {client.get('address_suburb', '')} {client.get('address_town', '')} {client.get('address_province', '')}",
                "PostalCode": client.get("postal_code", ""),
                "PrincipalTelephoneNumber": client["phone_number"],
                "PrincipalMemberEmailAddress": client.get("email", ""),
                "IncomeGroup": "L",
                "SpouseIndicator": "Y" if len(spouse) > 0 else "N",
                "NumberofAdultDependents": f"{number_of_dependencies}",
                "NumberofChildDependents": "",
                "NumberofExtendedFamily": "",
            }
            # add spouse if they exists
            if spouse:
                # split full name it first name middlename and last name
                full_name = spouse[0]["dependant_name"]
                full_name = full_name.split(" ")
                if len(full_name) == 1:
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = ""
                    details["SpouseSurname"] = ""
                    details["SpouseInitials"] = full_name[0]
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
