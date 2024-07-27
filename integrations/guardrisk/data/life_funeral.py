import json
from datetime import date, datetime

from config.models import Relationships, InsuranceCompany
from core.utils import get_initial_letter, get_loan_id_from_legacy_loan
from integrations.utils import get_frequency_number, populate_dependencies, is_new_policy

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


def prepare_life_funeral_payload(data: list, start_date: date, end_date: date, client_identifier):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")

    result = []
    relationships = Relationships.objects.all()
    print("Preparing funeral data...")
    for policy in data:
        try:
            if isinstance(policy["policy_details"], dict):
                policy_details = policy["policy_details"]
            else:
                policy_details = json.loads(policy["policy_details"])
        except json.JSONDecodeError as e:
            print(f'failed for policy id {policy["id"]}')
            policy_details = policy["policy_details"]

        client = policy["client"]
        policy_beneficiary = policy["policy_beneficiary"]
        policy_dependants = policy["policy_dependants"]
        # get spouse from dependants using relationship
        spouse_filter = filter(
            lambda x: x if relationships[x["relationship"]].name.lower() == "spouse" else None,
            policy_dependants,
        )
        spouse = list(spouse_filter)
        other_dependants = filter(
            lambda x: x if relationships[x["relationship"]].name.lower() != "spouse" else None,
            policy["policy_dependants"],
        )
        other_dependants = list(other_dependants)
        number_of_dependencies = len(other_dependants)
        insurer = policy["insurer"]
        if policy["is_legacy"]:
            division = policy_details.get("division_identifier")
            if policy["external_reference"]:
                policy_number = get_loan_id_from_legacy_loan(policy["external_reference"])
            else:
                policy_number = policy["policy_number"]
        else:
            division = policy.get("business_unit") or ""
            policy_number = policy["policy_number"]
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
            "ProductName": policy.get("product_name", ""),
            "ProductOption": product_option,
            "PolicyCommencementDate": policy.get("commencement_date", ""),
            "PolicyExpiryDate": policy.get("expiry_date", ""),
            "TermofPolicy": policy.get("policy_term", ""),
            "PolicyStatus": policy.get("policy_status", ""),
            "PolicyStatusDate": timestamp,
            "NewPolicyIndicator": is_new_policy(policy["created"]),
            "SalesChannel": policy_details.get("sales_channel", "Direct marketing via internet"),
            "CancelledbyPolicyholderCoolingPeriodInsurer": "N",
            "DeathIndicator": "Y",
            "PTDIndicator": "Y",
            "IncomeContinuationIndicator": "N",
            "PremiumFrequency": get_frequency_number(policy.get("premium_frequency", "Monthly")),
            "PremiumType": premium_type,
            "DeathOriginalSumAssured": policy.get("sum_insured"),
            "PTDOriginalSumAssured": policy.get("sum_insured"),
            "DeathCoverStructure": policy_details.get("death_cover_structure", "Lump sum"),
            "DeathCurrentSumAssured": policy.get("sum_insured"),
            "PTDCoverStructure": "Combined",
            "ReinsurerName": "N/A",
            "DeathCurrentRISumAssured": "N/A",
            "DeathRIPremium": "N/A",
            "DeathRIPercentage": "N/A",
            "TotalPolicyPremiumCollected": policy_details.get("total_policy_premium_collected", "0.00"),
            "TotalPolicyPremiumPayable": policy_details.get("total_loan_schedule", "0.00"),
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
            "PrincipalInitials":
                f"{get_initial_letter(client.get('first_name', ''))} {client.get('last_name', '')}",
            "PrincipalID": client.get("primary_id_number", ""),
            "PrincipalGender": client.get("gender", "U"),
            "PrincipalDateofBirth": client.get("date_of_birth", ""),
            "PrincipalMemberPhysicalAddress": f"{client.get('address_street', '')} {client.get('address_suburb', '')} "
                                              f"{client.get('address_town', '')} {client.get('address_province', '')}",
            "PostalCode": client.get("postal_code", ""),
            "PrincipalTelephoneNumber": client.get("phone_number", ""),
            "PrincipalMemberEmailAddress": client.get("email", ""),
            "IncomeGroup": "L",
            "SpouseIndicator": "Y" if len(spouse) > 0 else "N",
            "NumberofAdultDependents": f"{number_of_dependencies}",
            "NumberofChildDependents": "",
            "NumberofExtendedFamily": "",
        }
        # add spouse if they exists
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
        # populate_dependencies(other_dependants, details)

        result.append(details)
    # print(f'funeral request being sent :: {result}')
    return result
