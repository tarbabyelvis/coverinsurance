def prepare_life_claims_payload(data:list):
    result = []
    for item in data:
        result.append(
            {
                "TimeStamp": "sample text 1",
                "ReportPeriodStart": "sample text 2",
                "ReportPeriodEnd": "sample text 3",
                "AdministratorIdentifier": "sample text 4",
                "InsurerName": "sample text 5",
                "ClientIdentifier": "00123",
                "DivisionIdentifier": "0001",
                "SubSchemeName": "sample text 6",
                "PolicyNumber": "sample text 7",
                "PolicyCommencementDate": "sample text 8",
                "PolicyExpiryDate": "sample text 9",
                "TermOfPolicy": "sample text 10",
                "PolicyStatus": "sample text 11",
                "PolicyStatusDate": "sample text 12",
                "NewPolicyIndicator": "sample text 13",
                "ProductName": "sample text 14",
                "ProductOption": "sample text 15",
                "SalesChannel": "sample text 16",
                "ClaimInPeriod": "sample text 17",
                "ClaimStatus": "sample text 18",
                "ClaimStatusDate": "sample text 19",
                "ClaimNumberID": "sample text 20",
                "ClaimantIDNumber": "sample text 21",
                "ClaimEventDescription": "sample text 22",
                "ClaimType": "sample text 23",
                "DateOfClaimEvent": "sample text 24",
                "DateOfClaimFirstNotification": "sample text 25",
                "DateOfClaimFirstPayment": "sample text 26",
                "DateOfClaimLastPayment": "sample text 27",
                "CurrentMonthlyClaimPayment": "sample text 28",
                "ClaimEventCategory": "sample text 29",
                "TotalGrossClaimAmount": "sample text 30",
                "GrossClaimPaid": "sample text 31",
                "MemberClaiming": "sample text 32",
                "GrossClaims": "sample text 33",
                "PolicyWaitingPeriod": "sample text 34",
                "DeathCoverWaitingPeriod": "sample text 35",
                "PTDCoverWaitingPeriod": "sample text 36",
                "TTDCoverWaitingPeriod": "sample text 37",
                "IncomeContinuationCoverWaitingPeriod": "sample text 38",
                "DreadDiseaseCoverWaitingPeriod": "sample text 39",
                "RetrenchmentCoverWaitingPeriod": "sample text 40",
                "AccidentalDeathCoverWaitingPeriod": "sample text 41",
                "AccidentalInjuryCoverWaitingPeriod": "sample text 42",
                "IdentityTheftCoverWaitingPeriod": "sample text 43",
                "OtherAddOnRiderCoverWaitingPeriod": "sample text 44",
                "PotentialClaimAmountIfRepudiated": "sample text 45",
                "ReasonForRepudiation": "sample text 46",
                "ClaimRepudiated": "sample text 47",
                "DeathOriginalSumAssured": "sample text 48",
                "DeathCurrentSumAssured": "sample text 49",
                "DeathCurrentRISumAssured": "sample text 50",
                "PTDOriginalSumAssured": "sample text 51",
                "PTDCurrentSumAssured": "sample text 52",
                "PTDCurrentRISumAssured": "sample text 53",
                "IncomeContinuationOriginalSumAssured": "sample text 54",
                "IncomeContinuationCurrentSumAssured": "sample text 55",
                "IncomeContinuationCurrentRISumAssured": "sample text 56",
                "DreadDiseaseOriginalSumAssured": "sample text 57",
                "DreadDiseaseCurrentSumAssured": "sample text 58",
                "DreadDiseaseCurrentRISumAssured": "sample text 59",
                "RetrenchmentOriginalSumAssured": "sample text 60",
                "RetrenchmentCurrentSumAssured": "sample text 61",
                "RetrenchmentCurrentRISumAssured": "sample text 62",
                "PHICurrentSumAssured": "sample text 63",
                "PHIOriginalSumAssured": "sample text 64",
                "PHICurrentRISumAssured": "sample text 65",
                "MainMemberOriginalSumAssured": "sample text 66",
                "MainMemberDeathCurrentRISumAssured": "sample text 67",
                "SpouseOriginalSumAssured": "sample text 68",
                "SpouseDeathCurrentRISumAssured": "sample text 69",
                "Dependant1OriginalSumAssured": "sample text 70",
                "Dependant2OriginalSumAssured": "sample text 71",
                "Dependant3OriginalSumAssured": "sample text 72",
                "Dependant4OriginalSumAssured": "sample text 73",
                "Dependant5OriginalSumAssured": "sample text 74",
                "Dependant6OriginalSumAssured": "sample text 75",
                "Dependant7OriginalSumAssured": "sample text 76",
                "Dependant8OriginalSumAssured": "sample text 77",
                "Dependant9OriginalSumAssured": "sample text 78",
                "Dependant10OriginalSumAssured": "sample text 79",
                "Dependant11OriginalSumAssured": "sample text 80",
                "Dependant12OriginalSumAssured": "sample text 81",
                "Dependant13OriginalSumAssured": "sample text 82",
                "Dependant1DeathCurrentRISumAssured": "sample text 83",
                "Dependant2DeathCurrentRISumAssured": "sample text 84",
                "Dependant3DeathCurrentRISumAssured": "sample text 85",
                "Dependant4DeathCurrentRISumAssured": "sample text 86",
                "Dependant5DeathCurrentRISumAssured": "sample text 87",
                "Dependant6DeathCurrentRISumAssured": "sample text 88",
                "Dependant7DeathCurrentRISumAssured": "sample text 89",
                "Dependant8DeathCurrentRISumAssured": "sample text 90",
                "Dependant9DeathCurrentRISumAssured": "sample text 91",
                "Dependant10DeathCurrentRISumAssured": "sample text 92",
                "Dependant11DeathCurrentRISumAssured": "sample text 93",
                "Dependant12DeathCurrentRISumAssured": "sample text 94",
                "Dependant13DeathCurrentRISumAssured": "sample text 95",
                "TTDOriginalSumAssured": "sample text 96",
                "TTDCurrentSumAssured": "sample text 97",
                "TTDCurrentRISumAssured": "sample text 98",
                "HealthDreadDiseaseOriginalSumAssured": "sample text 99",
                "HealthDreadDiseaseCurrentSumAssured": "sample text 100",
                "HealthDreadDiseaseCurrentRISumAssured": "sample text 101",
                "AccidentalDeathOriginalSumAssured": "sample text 102",
                "AccidentalDeathCurrentSumAssured": "sample text 103",
                "AccidentalDeathCurrentRISumAssured": "sample text 104",
                "AccidentalInjuryOriginalSumAssured": "sample text 105",
                "AccidentalInjuryCurrentSumAssured": "sample text 106",
                "AccidentalInjuryCurrentRISumAssured": "sample text 107",
                "HospitalisationOriginalSumAssured": "sample text 108",
                "HospitalisationCurrentSumAssured": "sample text 109",
                "HospitalisationCurrentRISumAssured": "sample text 110",
                "CancerOriginalSumAssured": "sample text 111",
                "CancerCurrentSumAssured": "sample text 112",
                "CancerCurrentRISumAssured": "sample text 113",
                "IdentifyTheftOriginalSumAssured": "sample text 114",
                "IdentifyTheftCurrentSumAssured": "sample text 115",
                "IdentifyTheftCurrentRISumAssured": "sample text 116",
                "CashBackOriginalSumAssured": "sample text 117",
                "CashBackCurrentSumAssured": "sample text 118",
                "CashBackCurrentRISumAssured": "sample text 119",
                "OtherAddOnRiderOriginalSumAssured": "sample text 120",
                "OtherAddOnRiderCurrentSumAssured": "sample text 121",
                "OtherAddOnRiderCurrentRISumAssured": "sample text 122",
                "DeathCoverStructure": "sample text 123",
                "PTDCoverStructure": "sample text 124",
                "TTDCoverStructure": "sample text 125",
                "IncomeContinuationCoverStructure": "sample text 126",
                "DreadDiseaseCoverStructure": "sample text 127",
                "RetrenchmentCoverStructure": "sample text 128",
                "AccidentalDeathCoverStructure": "sample text 129",
                "AccidentalInjuryCoverStructure": "sample text 130",
                "IdentityTheftCoverStructure": "sample text 131",
                "MainMemberDeathCoverStructure": "sample text 132",
                "SpouseDeathCoverStructure": "sample text 133",
                "Dependant1DeathCoverStructure": "sample text 134",
                "Dependant2DeathCoverStructure": "sample text 135",
                "Dependant3DeathCoverStructure": "sample text 136",
                "Dependant4DeathCoverStructure": "sample text 137",
                "Dependant5DeathCoverStructure": "sample text 138",
                "Dependant6DeathCoverStructure": "sample text 139",
                "Dependant7DeathCoverStructure": "sample text 140",
                "Dependant8DeathCoverStructure": "sample text 141",
                "Dependant9DeathCoverStructure": "sample text 142",
                "Dependant10DeathCoverStructure": "sample text 143",
                "Dependant11DeathCoverStructure": "sample text 144",
                "Dependant12DeathCoverStructure": "sample text 145",
                "Dependant13DeathCoverStructure": "sample text 146",
                "OtherAddOnRiderCoverStructure": "sample text 147",
                "DeathCoverBenefitPaymentPeriod": "sample text 148",
                "PTDCoverBenefitPaymentPeriod": "sample text 149",
                "TTDCoverBenefitPaymentPeriod": "sample text 150",
                "IncomeContinuationCoverBenefitPaymentPeriod": "sample text 151",
                "DreadDiseaseCoverBenefitPaymentPeriod": "sample text 152",
                "RetrenchmentCoverBenefitPaymentPeriod": "sample text 153",
                "AccidentalDeathCoverBenefitPaymentPeriod": "sample text 154",
                "AccidentalInjuryCoverBenefitPaymentPeriod": "sample text 155",
                "IdentityTheftCoverBenefitPaymentPeriod": "sample text 156",
                "OtherAddOnRiderCoverBenefitPaymentPeriod": "sample text 157",
                "ReinsurerName": "sample text 158",
                "ReinsuranceRecoveries": "sample text 159",
                "RiskIdentifier": "sample text 160",
                "CancelledByPolicyholderCoolingPeriodInsurer": "sample text 161",
                "RepudiatedClaimDate": "sample text 162",
                "FreeText1": "sample text 163",
                "FreeText2": "sample text 164",
                "FreeText3": "sample text 165",
                "FreeText4": "sample text 166",
                "FreeText5": "sample text 167"
            }
        )

    return result
    

