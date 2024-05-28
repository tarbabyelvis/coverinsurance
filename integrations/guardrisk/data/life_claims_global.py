from integrations.utils import getFrequencyNumber


def prepare_life_claims_payload(data: list):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")
    result = []
    for claim in data:
        policy = claim["policy_id"]
        insurer = policy["insurer"]
        result.append(
            {
                "TimeStamp": timestamp,
                "ReportPeriodStart": start_date,
                "ReportPeriodEnd": end_date,
                "AdministratorIdentifier": "Getsure",
                "InsurerName": insurer.get("name", ""),
                "ClientIdentifier": "143",
                "DivisionIdentifier": "1",
                "SubSchemeName": "Getsure (Pty) Ltd",
                "PolicyNumber": policy["policy_number"],
                "PolicyCommencementDate": policy["commencement_date"],
                "PolicyExpiryDate": policy["expiry_date"],
                "TermOfPolicy": policy["policy_term"],
                "PolicyStatus": policy["policy_status"],
                "PolicyStatusDate":  policy["updated"],
                "NewPolicyIndicator": "P",
                "ProductName": policy["product_name"],
                "ProductOption": "N/A",
                "SalesChannel": "Voice Only",
                "ClaimInPeriod": "Y",
                "ClaimStatus": "O",
                "ClaimStatusDate": claim["updated"],
                "ClaimNumberID": claim["claimant_id_number"],
                "ClaimantIDNumber": claim["claimant_id_number"],
                "ClaimEventDescription": claim["claim_details"],
                "ClaimType": "L", // TODO add the claim type in model either L(Lumpsum) or I(Installment)
                "DateOfClaimEvent": claim["submitted-date"],
                "DateOfClaimFirstNotification": claim["submitted-date"],
                "DateOfClaimFirstPayment": claim["claim_paid_date"],
                "DateOfClaimLastPayment": claim["claim_paid_date"],
                "CurrentMonthlyClaimPayment": claim["claim_paid_date"], // TODO add claim monthly claim payment
                "ClaimEventCategory": claim["claim_type_id"], // TODO Death, PTD, TTD, PHI, Dread disease,
                "TotalGrossClaimAmount": claim["claim_amount"],
                "GrossClaimPaid": claim["claim_amount"], // TODO get the claim amount_paid
                "MemberClaiming": f({claim["name"]} {claim["surname"]}),
                "GrossClaims": claim["claim_amount"], //
                "PolicyWaitingPeriod": policy["waiting_period"], // TODO add policy waiting period
                "DeathCoverWaitingPeriod": policy["waiting_period"],
                "PTDCoverWaitingPeriod": policy["waiting_period"],
                "TTDCoverWaitingPeriod": policy["waiting_period"],
                "IncomeContinuationCoverWaitingPeriod": policy["waiting_period"],
                "DreadDiseaseCoverWaitingPeriod": policy["waiting_period"],
                "RetrenchmentCoverWaitingPeriod": policy["waiting_period"],
                "AccidentalDeathCoverWaitingPeriod": policy["waiting_period"],
                "AccidentalInjuryCoverWaitingPeriod": policy["waiting_period"],
                "IdentityTheftCoverWaitingPeriod": policy["waiting_period"],
                "OtherAddOnRiderCoverWaitingPeriod": policy["waiting_period"],
                "PotentialClaimAmountIfRepudiated": policy["waiting_period"],
                "ReasonForRepudiation": claim["repudiation_reason"], // TODO add repudiation_reason to claim
                "ClaimRepudiated": claim["claim_repudiated"], // TODO add field boolean
                "DeathOriginalSumAssured": claim["death_original_sum_assured"], // TODO add to policy or claim this field
                "DeathCurrentSumAssured": claim["death_original_sum_assured"],
                "DeathCurrentRISumAssured": claim["death_current_sum_assured"],
                "PTDOriginalSumAssured": claim["ptd_original_sum_assured"],
                "PTDCurrentSumAssured": claim["ptd_original_sum_assured"],
                "PTDCurrentRISumAssured": claim["ptd_original_sum_assured"],
                "IncomeContinuationOriginalSumAssured": claim["death_original_sum_assured"],
                "IncomeContinuationCurrentSumAssured": "N/A",
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
                "MainMemberOriginalSumAssured": policy["sum_insured"],
                "MainMemberDeathCurrentRISumAssured": policy["sum_insured"],
                "SpouseOriginalSumAssured": policy["sum_insured"],
                "SpouseDeathCurrentRISumAssured": policy["sum_insured"],
                "Dependant1OriginalSumAssured": policy["sum_insured"] ,
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
                "DeathCoverStructure": policy["cover_structure"] or "L",//TODO add to policy cover structure. L(Lumpsome) or M (monthly)
                "PTDCoverStructure": policy["cover_structure"] or "L",
                "TTDCoverStructure": policy["cover_structure"] or "L",
                "IncomeContinuationCoverStructure": policy["cover_structure"] or "L",
                "DreadDiseaseCoverStructure": policy["cover_structure"] or "L",
                "RetrenchmentCoverStructure": policy["cover_structure"] or "L",
                "AccidentalDeathCoverStructure": policy["cover_structure"] or "L",
                "AccidentalInjuryCoverStructure": policy["cover_structure"] or "L",
                "IdentityTheftCoverStructure": policy["cover_structure"] or "L",
                "MainMemberDeathCoverStructure": policy["cover_structure"] or "L",
                "SpouseDeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant1DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant2DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant3DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant4DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant5DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant6DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant7DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant8DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant9DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant10DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant11DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant12DeathCoverStructure": policy["cover_structure"] or "L",
                "Dependant13DeathCoverStructure": policy["cover_structure"] or "L",
                "OtherAddOnRiderCoverStructure": policy["cover_structure"] or "L",
                "DeathCoverBenefitPaymentPeriod": claim["benefit_payment_period"],//TODO add benefit_payment_period
                "PTDCoverBenefitPaymentPeriod": claim["benefit_payment_period"],
                "TTDCoverBenefitPaymentPeriod": claim["benefit_payment_period"],
                "IncomeContinuationCoverBenefitPaymentPeriod": claim["installments_paid"],//TODO add installments_paid (1 for a lumpsome payments or more for monthly payments)
                "DreadDiseaseCoverBenefitPaymentPeriod": claim["installments_paid"],
                "RetrenchmentCoverBenefitPaymentPeriod": claim["installments_paid"],
                "AccidentalDeathCoverBenefitPaymentPeriod": claim["installments_paid"],
                "AccidentalInjuryCoverBenefitPaymentPeriod": claim["installments_paid"],
                "IdentityTheftCoverBenefitPaymentPeriod": claim["installments_paid"],
                "OtherAddOnRiderCoverBenefitPaymentPeriod": claim["installments_paid"],
                "ReinsurerName": "N/A",
                "ReinsuranceRecoveries": "N/A",
                "RiskIdentifier": "N/A",
                "CancelledByPolicyholderCoolingPeriodInsurer": "N/A",
                "RepudiatedClaimDate": claim["repudiated_claim_date"],
                "FreeText1": claim["comments"] or "",
                "FreeText2": "N/A",
                "FreeText3": "N/A",
                "FreeText4": "N/A",
                "FreeText5": "N/A"
            }
        )

    return result
