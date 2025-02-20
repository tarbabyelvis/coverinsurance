from datetime import date, datetime

from clients.models import ClientDetails
from config.models import InsuranceCompany
from integrations.utils import generate_payment_reference, calculate_vat_amount, calculate_amount_excluding_vat, \
    calculate_guard_risk_admin_amount


def prepare_premium_payload(
        data: list, start_date: date, end_date: date
):
    original_date = datetime.now()
    timestamp = original_date.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")
    end_date = end_date.strftime("%Y/%m/%d")
    result = []
    print("Preparing payment data")
    for payment in data:
        policy = payment["policy"]
        client = policy["client"]
        client = ClientDetails.objects.filter(pk=client).first()
        insurer = policy["insurer"]
        insurer = InsuranceCompany.objects.filter(pk=insurer).first()
        premium_amount = float(payment["amount"])
        vat_amount = calculate_vat_amount(premium_amount)
        premium_less_vat = calculate_amount_excluding_vat(premium_amount, vat_amount)
        guardrisk_amount = calculate_guard_risk_admin_amount(premium_amount)
        commission = calculate_insurer_commission_amount(premium_amount)
        binder_fee = calculate_binder_fee_amount(premium_amount)
        nett_amount = calculate_nett_amount(premium_amount, guardrisk_amount, commission, binder_fee)
        details = {
            "DateReportRun": timestamp,
            "ReportPeriodFrom": start_date,
            "ReportPeriodTo": end_date,
            "RevisionNumber": "",
            "FacilityNumberCellId": "",
            "TransactionIDRecordUniqueIdentifier": payment.get("payment_reference",
                                                               generate_payment_reference(
                                                                   policy_number=policy["policy_number"],
                                                                   payment_date=payment["payment_date"])),
            "PayFrequency": "Monthly",
            "CurrencyIndicator": payment.get("currency", "ZAR"),
            "VatonPremium": vat_amount,
            "PremiumExVat": premium_less_vat,
            "PremiumInclVat": premium_amount,
            "NettPremium": nett_amount,
            "Sasria": "No",
            "SasriaInsurerCommission": "",
            "SasriaBrokerCommission": "",
            "SasriaCommission": "",
            "NettSasria": "",
            "TotalCollected": premium_amount,
            "PolicyNumber": policy["policy_number"],
            "ProductID": policy["policy_number"],
            "ProductName": policy["product_name"],
            "Cover": policy["product_name"],
            "SubCover": policy["product_name"],
            "Type": policy["product_name"],
            "SumInsuredforProduct": policy.get("sum_insured"),
            "PolicyLimit": "",  # total repayment amount
            "CoverLimit": "",
            "ExcessDeductible": "",
            "OriginalInception": policy["commencement_date"],
            "LastRenewalDate": "",
            "NextRenewalDate": "",
            "StartDateProductCover": payment["payment_date"],
            "EndDateProductCover": payment["payment_date"],
            "StatusoftheProduct": policy["policy_status"],
            "DateofStatus": timestamp,
            "InsuredEntity": "",
            "InsuredIDRegistrationNumber": client.primary_id_number,
            "Surname": client.last_name,
            "GivenName": client.first_name or "" + " " + client.middle_name or "",
            "EmailAddress": client.email,
            "ContactNumber": client.phone_number,
            "RiskAddressLine1": client.address_street,
            "RiskAddressLine2": client.address_street,
            "RiskAddressLine3": client.address_suburb,
            "RiskAddressLine4": client.address_town,
            "RiskAddressLine5": "South Africa",
            "RiskAddressPostalCode": client.postal_code or "",
            "ResidenceType": "",
            "GPSCoordinatesLongitude": "",
            "GPSCoordinatesLatitude": "",
            "DriverGender": client.gender,
            "Language": "English",
            "DriverDateofBirth": "",
            "DriversLicenseCode": "",
            "DriversLicenseDate": "",
            "VehicleVINNumber": "",
            "VehicleRegistrationNumber": "",
            "YearofManufacture": "",
            "VehicleMMCode": "",
            "VehicleColour": "",
            "TypeofVessel": "",
            "TerritorialLimits": "",
            "LegalEntityNameProvidingReport": "Fin",
            "LegalEntityAddress": "",
            "LegalEntityCompanyRegistrationNumber": "",
            "LegalEntityVatNo": "",
            "Insurer": insurer.name,
            "FSPName": "",
            "FSPNumber": "",
            "IGFNameofPartyIssuedTo": "",
            "IGFGuaranteeNumberIssue": "",
            "DiscountsLoadingLevelofDiscounttoBaseRate": "",
            "SalesChannel": "Direct marketing via internet",
            "TransactionType": payment.get("transaction_type", ""),
            "Administrator": policy["entity"],
            "Brokerage": "",
            "FreeText1": "",
        }
        result.append(details)
    return result


def calculate_insurer_commission_amount(premium_amount: float) -> float:
    return round(0.075 * premium_amount, 2)


def calculate_binder_fee_amount(premium_amount: float) -> float:
    return round(0.09 * premium_amount, 2)


def calculate_nett_amount(premium_amount: float,
                          guardrisk_amount: float,
                          commission: float,
                          binder_fee: float) -> float:
    return round((premium_amount - guardrisk_amount - commission - binder_fee), 2)
