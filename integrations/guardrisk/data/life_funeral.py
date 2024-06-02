import json
from datetime import date, datetime

from config.models import Relationships
from core.utils import get_initial_letter
from integrations.utils import get_frequency_number, populate_dependencies

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
            print('1st stage ,,,')
            insurer = policy["insurer"]
            client = policy["client"]
            policy_beneficiary = policy["policy_beneficiary"]
            policy_dependants = policy["policy_dependants"]
            no_of_dependencies = len(policy_dependants)
            print(f'number of dependencies: {no_of_dependencies}')
            # get spouse from dependants using relationship
            spouse_filter = filter(
                lambda x: x if relationships[x["relationship"]].name.lower() == "spouse" else None,
                policy_dependants,
            )
            spouse = list(spouse_filter)
            other_dependants = filter(
                lambda x: x if relationships[x["relationship"]].lower() != "spouse" else None,
                policy["policy_dependants"],
            )
            other_dependants = list(other_dependants)
            number_of_dependencies = len(other_dependants)
            insurer = policy["insurer"]
            print(f'no of dependencies: {number_of_dependencies}')
            details = {
                "TimeStamp": timestamp,
                "ReportPeriodStart": start_date,
                "ReportPeriodEnd": end_date,
                "AdministratorIdentifier": "Getsure",
                "InsurerName": insurer.get("name", ""),
                "ClientIdentifier": "143",
                "DivisionIdentifier": division_identifier,
                "SubSchemeName": "Getsure (Pty) Ltd",
                "PolicyNumber": policy.get("policy_number", ""),
                "ProductName": policy.get("product_name", ""),
                "ProductOption": product_option,
                "PolicyCommencementDate": policy.get("commencement_date", ""),
                "PolicyExpiryDate": policy.get("expiry_date", ""),
                "TermofPolicy": policy.get("policy_term", ""),
                "PolicyStatus": policy.get("policy_status", ""),
                "PolicyStatusDate": policy_details.get("policy_status_date", ""),
                "NewPolicyIndicator": policy_details.get("new_policy_indicator", "P"),
                "SalesChannel": policy_details.get("sales_channel", "Direct marketing via internet"),
                "CancelledbyPolicyholderCoolingPeriodInsurer": "",
                "DeathIndicator": policy_details.get("death_indicator", "Y"),
                "PTDIndicator": "Y",
                "IncomeContinuationIndicator": "N",
                "PremiumFrequency": get_frequency_number(policy.get("premium_frequency", "Monthly")),
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
                "CommissionFrequency": get_frequency_number(policy.get("commission_frequency", "Monthly")),
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
                "PrincipalTelephoneNumber": client.get("phone_number", ""),
                "PrincipalMemberEmailAddress": client.get("email", ""),
                "IncomeGroup": "L",
                "SpouseIndicator": "Y" if len(spouse) > 0 else "N",
                "NumberofAdultDependents": f"{number_of_dependencies}",
                "NumberofChildDependents": "",
                "NumberofExtendedFamily": "",
            }
            print('details built,,,')
            # add spouse if they exists
            if spouse:
                print('in spouse true')
                print(f'spouse: {spouse}')
                # split full name it first name middlename and last name
                full_name = spouse[0]["dependant_name"]
                print('full name built,,,')
                full_name = full_name.split(" ")
                if len(full_name) == 1:
                    print('in name 1...')
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = ""
                    details["SpouseSurname"] = ""
                    details["SpouseInitials"] = full_name[0]
                elif len(full_name) == 2:
                    print('in name 2...')
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = ""
                    details["SpouseSurname"] = full_name[1]
                    details["SpouseInitials"] = f"{full_name[0][0]} {full_name[1][0]}"
                elif len(full_name) == 3:
                    print('in name 3...')
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = full_name[1]
                    details["SpouseSurname"] = full_name[2]
                    details["SpouseInitials"] = f"{full_name[0][0]} {full_name[1][0]} {full_name[2][0]}"
                else:
                    print('in name else...')
                    details["SpouseFirstName"] = full_name[0]
                    details["SpouseMiddleName"] = " ".join(full_name[1:-1])
                    details["SpouseSurname"] = full_name[-1]
                    details["SpouseInitials"] = f" {full_name[0][0]} {full_name[1][0]} {full_name[-1][0]}"

                spouse = spouse[0]
                details["SpouseID"] = spouse.get("primary_id_number", "")
                details["SpouseGender"] = spouse.get("dependant_gender")
                details["SpouseDateofBirth"] = spouse.get("dependant_dob")
                details["SpouseCoverAmount"] = spouse.get("cover_amount", "0.00")
                details["SpouseCoverCommencementDate"] = spouse.get("cover_commencement_date", "0.00")
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

                # add dependants of they exists
            print('did we get past dependencies...')
            print(f'other deps len: {len(other_dependants)}')
            populate_dependencies(other_dependants, details)

            result.append(details)

    return result
