import json
import logging
from datetime import date, datetime

from config.models import InsuranceCompany
from integrations.utils import is_new_policy, generate_claim_reference

log = logging.getLogger(__name__)

product_option = "all"
premium_type = "Regular"
death_cover_structure = "L"
ptd_cover_structure = "L"
retrenchment_cover_structure = "L"
death_cover_benefit_payment_period = 1
ptd_cover_benefit_payment_period = 1
income_continuation_cover_benefit_payment_period = 1
retrenchment_death_payment_period = 30
death_waiting_period = 3
ptd_waiting_period = 3
waiting_period = 3
retrenchment_waiting_period = 6


def prepare_life_claims_payload(data: list, start_date: date, end_date: date, client_identifier):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")
    result = []
    for claim in data:
        print(f'claim {claim}')
        policy = claim["policy"]
        insurer = policy["insurer"]
        insurer = InsuranceCompany.objects.filter(pk=insurer).first()
        try:
            if isinstance(policy["policy_details"], dict):
                policy_details = policy["policy_details"]
            else:
                policy_details = json.loads(policy["policy_details"])
        except json.JSONDecodeError as e:
            policy_details = policy["policy_details"]

        claim_details = {
            "TimeStamp": timestamp,
            "ReportPeriodStart": start_date,
            "ReportPeriodEnd": end_date,
            "AdministratorIdentifier": policy["entity"],
            "InsurerName": insurer.name,
            "ClientIdentifier": client_identifier,
            "DivisionIdentifier": policy_details.get("division_identifier", "2"),
            "SubSchemeName": policy["sub_scheme"],
            "PolicyNumber": policy["policy_number"],
            "PolicyCommencementDate": policy["commencement_date"],
            "PolicyExpiryDate": policy["expiry_date"],
            "TermOfPolicy": policy["policy_term"],
            "PolicyStatus": policy["policy_status"],
            "PolicyStatusDate": timestamp,
            "NewPolicyIndicator": is_new_policy(policy["created"]),
            "ProductName": policy["product_name"],
            "ProductOption": product_option,
            "SalesChannel": policy_details.get("sales_channel", ""),
            "ClaimInPeriod": "Y",  # TODO check dynamically
            "ClaimStatus": claim["claim_status"],
            "ClaimStatusDate": timestamp,
            "ClaimNumberID": generate_claim_reference(claim["claimant_id_number"],
                                                      policy_number=policy["policy_number"]),
            "ClaimantIDNumber": claim["claimant_id_number"],
            "ClaimEventDescription": "",
            "ClaimType": "L",  # TODO add the claim type in model either L(Lumpsum) or I(Installment)
            "DateOfClaimEvent": claim["submitted_date"],
            "DateOfClaimFirstNotification": claim["submitted_date"],
            "DateOfClaimFirstPayment": claim["claim_paid_date"],
            "DateOfClaimLastPayment": claim["claim_paid_date"],  # TODO check the correct date
            "CurrentMonthlyClaimPayment": claim["claim_amount"],  # TODO add claim monthly claim payment
            "ClaimEventCategory": claim["claim_type"]["name"],  # TODO Death, PTD, TTD, PHI, Dread disease,
            "TotalGrossClaimAmount": claim["claim_amount"],
            "GrossClaimPaid": claim["claim_amount"],  # TODO get the claim amount_paid
            "MemberClaiming": f'{claim["claimant_name"]} {claim["claimant_surname"]}',
            "GrossClaims": claim["claim_amount"],
            "PolicyWaitingPeriod": death_waiting_period,  # TODO add policy waiting period
            "DeathCoverWaitingPeriod": death_waiting_period,
            "PTDCoverWaitingPeriod": ptd_waiting_period,
            "TTDCoverWaitingPeriod": waiting_period,
            "IncomeContinuationCoverWaitingPeriod": waiting_period,
            "DreadDiseaseCoverWaitingPeriod": waiting_period,
            "RetrenchmentCoverWaitingPeriod": retrenchment_waiting_period,
            "AccidentalDeathCoverWaitingPeriod": death_waiting_period,
            "AccidentalInjuryCoverWaitingPeriod": waiting_period,
            "IdentityTheftCoverWaitingPeriod": waiting_period,
            "OtherAddOnRiderCoverWaitingPeriod": waiting_period,
            "PotentialClaimAmountIfRepudiated": claim["claim_amount"],
            "ReasonForRepudiation": claim.get("repudiated_reason", ""),
            "ClaimRepudiated": "Y" if claim.get("claim_repudiated") else "N",
            "DeathOriginalSumAssured": policy.get("sum_insured"),
            "DeathCurrentSumAssured": policy_details.get("death_current_sum_insured", policy.get("sum_insured")),
            "DeathCurrentRISumAssured": policy_details.get("death_current_ri_sum_insured", policy.get("sum_insured")),
            "PTDOriginalSumAssured": policy_details.get("death_current_sum_insured", policy.get("sum_insured")),
            "PTDCurrentSumAssured": claim.get("ptd_current_sum_assured", policy.get("sum_insured")),
            "PTDCurrentRISumAssured": claim.get("ptd_current_sum_assured", policy.get("sum_insured")),
            "IncomeContinuationOriginalSumAssured": policy.get("sum_insured"),
            "IncomeContinuationCurrentSumAssured": policy.get("sum_insured"),
            "IncomeContinuationCurrentRISumAssured": "N/A",
            "DreadDiseaseOriginalSumAssured": "N/A",
            "DreadDiseaseCurrentSumAssured": "N/A",
            "DreadDiseaseCurrentRISumAssured": "N/A",
            "RetrenchmentOriginalSumAssured": "N/A",
            "RetrenchmentCurrentSumAssured": "N/A",
            "RetrenchmentCurrentRISumAssured": "N/A",
            "PHICurrentSumAssured": "N/A",
            "PHIOriginalSumAssured": "N/A",
            "PHICurrentRISumAssured": "N/A",
            "MainMemberOriginalSumAssured": policy_details.get("death_original_sum_assured", ""),
            "MainMemberDeathCurrentRISumAssured": policy["sum_insured"],
            "SpouseOriginalSumAssured": policy["sum_insured"],
            "SpouseDeathCurrentRISumAssured": policy["sum_insured"],
            "Dependant1OriginalSumAssured": policy["sum_insured"],
            "Dependant2OriginalSumAssured": "N/A",
            "Dependant3OriginalSumAssured": "N/A",
            "Dependant4OriginalSumAssured": "N/A",
            "Dependant5OriginalSumAssured": "N/A",
            "Dependant6OriginalSumAssured": "N/A",
            "Dependant7OriginalSumAssured": "N/A",
            "Dependant8OriginalSumAssured": "N/A",
            "Dependant9OriginalSumAssured": "N/A",
            "Dependant10OriginalSumAssured": "N/A",
            "Dependant11OriginalSumAssured": "N/A",
            "Dependant12OriginalSumAssured": "N/A",
            "Dependant13OriginalSumAssured": "N/A",
            "Dependant1DeathCurrentRISumAssured": "N/A",
            "Dependant2DeathCurrentRISumAssured": "N/A",
            "Dependant3DeathCurrentRISumAssured": "N/A",
            "Dependant4DeathCurrentRISumAssured": "N/A",
            "Dependant5DeathCurrentRISumAssured": "N/A",
            "Dependant6DeathCurrentRISumAssured": "N/A",
            "Dependant7DeathCurrentRISumAssured": "N/A",
            "Dependant8DeathCurrentRISumAssured": "N/A",
            "Dependant9DeathCurrentRISumAssured": "N/A",
            "Dependant10DeathCurrentRISumAssured": "N/A",
            "Dependant11DeathCurrentRISumAssured": "N/A",
            "Dependant12DeathCurrentRISumAssured": "N/A",
            "Dependant13DeathCurrentRISumAssured": "N/A",
            "TTDOriginalSumAssured": policy["sum_insured"],
            "TTDCurrentSumAssured": policy["sum_insured"],
            "TTDCurrentRISumAssured": policy["sum_insured"],
            "HealthDreadDiseaseOriginalSumAssured": policy["sum_insured"],
            "HealthDreadDiseaseCurrentSumAssured": policy["sum_insured"],
            "HealthDreadDiseaseCurrentRISumAssured": policy["sum_insured"],
            "AccidentalDeathOriginalSumAssured": policy["sum_insured"],
            "AccidentalDeathCurrentSumAssured": policy["sum_insured"],
            "AccidentalDeathCurrentRISumAssured": policy["sum_insured"],
            "AccidentalInjuryOriginalSumAssured": policy["sum_insured"],
            "AccidentalInjuryCurrentSumAssured": policy["sum_insured"],
            "AccidentalInjuryCurrentRISumAssured": policy["sum_insured"],
            "HospitalisationOriginalSumAssured": policy["sum_insured"],
            "HospitalisationCurrentSumAssured": policy["sum_insured"],
            "HospitalisationCurrentRISumAssured": policy["sum_insured"],
            "CancerOriginalSumAssured": policy["sum_insured"],
            "CancerCurrentSumAssured": policy["sum_insured"],
            "CancerCurrentRISumAssured": policy["sum_insured"],
            "IdentifyTheftOriginalSumAssured": policy["sum_insured"],
            "IdentifyTheftCurrentSumAssured": policy["sum_insured"],
            "IdentifyTheftCurrentRISumAssured": policy["sum_insured"],
            "CashBackOriginalSumAssured": policy["sum_insured"],
            "CashBackCurrentSumAssured": policy["sum_insured"],
            "CashBackCurrentRISumAssured": policy["sum_insured"],
            "OtherAddOnRiderOriginalSumAssured": policy["sum_insured"],
            "OtherAddOnRiderCurrentSumAssured": policy["sum_insured"],
            "OtherAddOnRiderCurrentRISumAssured": policy["sum_insured"],
            "DeathCoverStructure": policy_details.get("death_cover_structure", death_cover_structure),
            "PTDCoverStructure": ptd_cover_structure,
            "TTDCoverStructure": ptd_cover_structure,
            "IncomeContinuationCoverStructure": policy.get("cover_structure", "L"),
            "DreadDiseaseCoverStructure": policy.get("cover_structure", "L"),
            "RetrenchmentCoverStructure": policy.get("cover_structure", "L"),
            "AccidentalDeathCoverStructure": policy.get("cover_structure", "L"),
            "AccidentalInjuryCoverStructure": policy.get("cover_structure", "L"),
            "IdentityTheftCoverStructure": policy.get("cover_structure", "L"),
            "MainMemberDeathCoverStructure": policy.get("cover_structure", "L"),
            "SpouseDeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant1DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant2DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant3DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant4DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant5DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant6DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant7DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant8DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant9DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant10DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant11DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant12DeathCoverStructure": policy.get("cover_structure", "L"),
            "Dependant13DeathCoverStructure": policy.get("cover_structure", "L"),
            "OtherAddOnRiderCoverStructure": policy.get("cover_structure", "L"),
            "DeathCoverBenefitPaymentPeriod": death_cover_benefit_payment_period,  # TODO add benefit_payment_period
            "PTDCoverBenefitPaymentPeriod": ptd_cover_benefit_payment_period,
            "TTDCoverBenefitPaymentPeriod": ptd_cover_benefit_payment_period,
            "IncomeContinuationCoverBenefitPaymentPeriod": income_continuation_cover_benefit_payment_period,
            "DreadDiseaseCoverBenefitPaymentPeriod": income_continuation_cover_benefit_payment_period,
            "RetrenchmentCoverBenefitPaymentPeriod": income_continuation_cover_benefit_payment_period,
            "AccidentalDeathCoverBenefitPaymentPeriod": death_cover_benefit_payment_period,
            "AccidentalInjuryCoverBenefitPaymentPeriod": income_continuation_cover_benefit_payment_period,
            "IdentityTheftCoverBenefitPaymentPeriod": income_continuation_cover_benefit_payment_period,
            "OtherAddOnRiderCoverBenefitPaymentPeriod": income_continuation_cover_benefit_payment_period,
            "ReinsurerName": "N/A",
            "ReinsuranceRecoveries": "N/A",
            "RiskIdentifier": "N/A",
            "CancelledByPolicyholderCoolingPeriodInsurer": "N/A",
            "RepudiatedClaimDate": claim.get("repudiated_date", ""),
            "FreeText1": claim.get("comments", ""),
            "FreeText2": "N/A",
            "FreeText3": "N/A",
            "FreeText4": "N/A",
            "FreeText5": "N/A",
        }
        result.append(claim_details)
    return result
