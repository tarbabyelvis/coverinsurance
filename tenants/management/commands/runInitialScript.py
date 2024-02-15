from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from loans.models import (
    LoanStage,
    LoanType,
    LoanPriority,
    PaymentModes,
    Teams,
    TypeOfBusiness,
    LoanRejectionReasons,
    LoanPurpose,
    EmploymentStatus,
    DocumentTypes,
    LoanProduct,
    Currency,
    ProductConsents,
    DestinationAccount,
    Loan,
)
from leads.models import ReasonForClosing
from validations.models import BridgeValidation
from tenants.models import Integration
from sms.models import CommsTemplate


class Command(BaseCommand):
    help = "Migrate Initial DB script for new tenant setup e.g. ./manage.py tenant_command runInitialScript --schema=fin_tz"

    def add_arguments(self, parser):
        parser.add_argument("--schema", nargs="+", type=str)

    def handle(self, *args, **options):
        print(options)
        # Initialising Loan Teams
        try:
            teams = Teams.objects.filter()
            if teams.__len__() == 0:
                print("No teams! Initialising teams...")
                Teams.objects.bulk_create(
                    [
                        Teams(id=1, name="Sales"),
                        Teams(id=2, name="Credit Analysis"),
                        Teams(id=3, name="Credit Admin"),
                        Teams(id=4, name="Finance"),
                    ]
                )
                message5 = "Successfully Initialised Teams"
                print(message5)
            else:
                message5 = "Teams already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Loan Stages
        try:
            loan_stages = LoanStage.objects.filter()
            if loan_stages.__len__() == 0:
                print("No Loan Stages found! Initialising stages...")
                LoanStage.objects.bulk_create(
                    [
                        LoanStage(
                            id=1,
                            name="DECLINED",
                            color="#ff0000",
                            client_status_desc="Declined",
                        ),
                        LoanStage(
                            id=2,
                            name="INCOMPLETE",
                            color="#E56A55",
                            team_id=1,
                            client_status_desc="Document Verification",
                        ),
                        LoanStage(
                            id=3,
                            name="QUALITY CHECK",
                            color="#41B49B",
                            team_id=2,
                            client_status_desc="Processing Application",
                        ),
                        LoanStage(
                            id=4,
                            name="CALL BACK",
                            color="#215a4e",
                            team_id=2,
                            client_status_desc="Application Processing",
                        ),
                        LoanStage(
                            id=5,
                            name="CREDIT COMM / APPROVAL",
                            color="#19BFD3",
                            team_id=2,
                            client_status_desc="Security Processing",
                        ),
                        LoanStage(
                            id=6,
                            name="SETTLEMENT OF THIRD-PARTY LOANS",
                            color="#0a4c54",
                            team_id=3,
                            client_status_desc="Security Processing",
                        ),
                        LoanStage(
                            id=7,
                            name="THIRD-PARTY CLEARANCE",
                            color="#F1A91E",
                            team_id=3,
                            client_status_desc="Security Processing",
                        ),
                        LoanStage(
                            id=8,
                            name="SECURITY PERFECTION",
                            color="#215a4e",
                            team_id=3,
                            client_status_desc="Security Processing",
                        ),
                        LoanStage(
                            id=9,
                            name="DISBURSEMENT",
                            color="#215a4e",
                            team_id=4,
                            client_status_desc="Pending Disbursement",
                        ),
                        LoanStage(
                            id=20,
                            name="PENDING SUBMISSION",
                            color="#73352b",
                            client_status_desc="Pending Submission",
                        ),
                    ]
                )
                message = "Successfully Initiased Loan Stages."
                print(message)
            else:
                message = "Loan stages already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising LoanTypes
        try:
            laon_types = LoanType.objects.filter()
            if laon_types.__len__() == 0:
                print("No Loan Types found! Initialising types...")
                LoanType.objects.bulk_create(
                    [
                        LoanType(id=1, name="Straight Loan"),
                        LoanType(id=2, name="Refinance"),
                        LoanType(id=3, name="Third-party Buyoff"),
                        LoanType(id=4, name="Refinance + Buyoff"),
                    ]
                )
                message2 = "Successfully Initiased Loan Types."
                print(message2)
            else:
                message2 = "Loan stages already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Priority
        try:
            laon_priorities = LoanPriority.objects.filter()
            if laon_priorities.__len__() == 0:
                print("No Loan Priorities found! Initialising priority...")
                LoanPriority.objects.bulk_create(
                    [LoanPriority(id=1, name="High"), LoanPriority(id=2, name="Normal")]
                )
                message3 = "Successfully Initiased Loan Loan Priority."
                print(message3)
            else:
                message3 = "Loan priority already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Payment Modes
        try:
            payment_modes = PaymentModes.objects.filter()
            if payment_modes.__len__() == 0:
                print("No Payment Modes found! Initialising payment modes...")
                PaymentModes.objects.bulk_create(
                    [
                        PaymentModes(id=1, name="M-Pesa"),
                        PaymentModes(id=2, name="Bank"),
                        PaymentModes(id=3, name="Cheque"),
                        PaymentModes(id=4, name="Standing Order"),
                    ]
                )
                message4 = "Successfully Initiased Payment modes."
                print(message4)
            else:
                message4 = "Payment modes already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Type of Business Teams
        try:
            business = TypeOfBusiness.objects.filter()
            if business.__len__() == 0:
                print("No type of business! Initialising type of business...")
                TypeOfBusiness.objects.bulk_create(
                    [
                        TypeOfBusiness(id=1, name="Tendering and Contracting"),
                        TypeOfBusiness(id=2, name="Retail Shop"),
                        TypeOfBusiness(id=3, name="Medical Services"),
                        TypeOfBusiness(id=4, name="Building and Construction"),
                        TypeOfBusiness(
                            id=5, name="Event Planning, Marketing and Branding"
                        ),
                        TypeOfBusiness(id=6, name="Transport and Logistics"),
                        TypeOfBusiness(id=7, name="Farming"),
                        TypeOfBusiness(id=8, name="Investment and Property Management"),
                        TypeOfBusiness(id=9, name="Insurance Brokerage"),
                        TypeOfBusiness(id=10, name="Auctioneering"),
                        TypeOfBusiness(
                            id=11, name="Business Consultancy and Support Services"
                        ),
                        TypeOfBusiness(id=12, name="Car Dealership"),
                        TypeOfBusiness(id=13, name="School Development"),
                        TypeOfBusiness(id=14, name="Healthcare"),
                        TypeOfBusiness(id=15, name="Hotel and Restaurant"),
                        TypeOfBusiness(id=16, name="Supplies and Distribution"),
                    ]
                )
                message6 = "Successfully Initialised Types of Business"
                print(message6)
            else:
                message6 = "Type of busines already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Loan Rejection Reasons
        try:
            rejections = LoanRejectionReasons.objects.filter()
            if rejections.__len__() == 0:
                print("No rejection reasons! Initialising rejection reasons...")
                LoanRejectionReasons.objects.bulk_create(
                    [
                        LoanRejectionReasons(id=1, text="No Affordability"),
                        LoanRejectionReasons(id=2, text="No MOU"),
                        LoanRejectionReasons(id=3, text="Declined By Client"),
                        LoanRejectionReasons(id=4, text="Declined by Employer"),
                        LoanRejectionReasons(id=5, text="Incomplete"),
                        LoanRejectionReasons(id=6, text="Call back not sucessfull"),
                        LoanRejectionReasons(id=7, text="Duplicate record"),
                        LoanRejectionReasons(id=8, text="Declined"),
                    ]
                )
                message7 = "Successfully Initialised Loan Rejection Reasons"
                print(message7)
            else:
                message7 = "Rejections reasons already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Loan Purpose
        try:
            rejections = LoanPurpose.objects.filter()
            if rejections.__len__() == 0:
                print("No loan purpose! Initialising loan purposes...")
                LoanPurpose.objects.bulk_create(
                    [
                        LoanPurpose(
                            id=1,
                            purpose="Personal",
                            code="O",
                            reason_code="Other",
                            description="A loan other than the ones stipulated above.",
                        ),
                        LoanPurpose(
                            id=2,
                            purpose="Asset Finance",
                            code="F",
                            reason_code="Other Asset acquisition financing",
                            description="Financing of fixed or moveable asset other than property",
                        ),
                        LoanPurpose(
                            id=3,
                            purpose="Education",
                            code="S",
                            reason_code="Study Loan",
                            description="Loan to fund formal studies at a recognised institution",
                        ),
                        LoanPurpose(
                            id=4,
                            purpose="Family Support",
                            code="O",
                            reason_code="Other",
                            description="A loan other than the ones stipulated above.",
                        ),
                        LoanPurpose(
                            id=5,
                            purpose="Medical Emergency",
                            code="E",
                            reason_code="Crisis Loan",
                            description="Loan granted to overcome client cash flow problems during unforeseen circumstances: Medical",
                        ),
                        LoanPurpose(
                            id=6,
                            purpose="Business Working Capital",
                            code="J",
                            reason_code="Small Business",
                            description="A loan to a sole proprietor",
                        ),
                        LoanPurpose(
                            id=7,
                            purpose="Other Emergency",
                            code="C",
                            reason_code="Crisis Loan",
                            description="Loan granted to overcome client cash flow problems during unforeseen circumstances: Other Emergency",
                        ),
                        LoanPurpose(
                            id=8,
                            purpose="Death-Funeral",
                            code="D",
                            reason_code="Crisis Loan",
                            description="Loan granted to overcome client cash flow problems during unforeseen circumstances: Death or Funeral",
                        ),
                        LoanPurpose(
                            id=9,
                            purpose="Income Loss",
                            code="G",
                            reason_code="Crisis Loan",
                            description="Loan granted to overcome client cash flow problems during unforeseen circumstances: Income Loss",
                        ),
                        LoanPurpose(
                            id=10,
                            purpose="Theft or Fire",
                            code="I",
                            reason_code="Crisis Loan",
                            description="Loan granted to overcome client cash flow problems during unforeseen circumstances: Loss - Theft or Fire",
                        ),
                        LoanPurpose(
                            id=11,
                            purpose="Home Loans",
                            code="H",
                            reason_code="Home Loans",
                            description="New property acquisition or upgrades to existing property",
                        ),
                        LoanPurpose(
                            id=12,
                            purpose="Other",
                            code="O",
                            reason_code="Other",
                            description="A loan other than the ones stipulated above.",
                        ),
                    ]
                )
                message8 = "Successfully Initialised Loan Purpose"
                print(message8)
            else:
                message8 = "Loan purposes already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Employment Status
        try:
            employment = EmploymentStatus.objects.filter()
            if employment.__len__() == 0:
                print("No employment status! Initialising employment status...")
                EmploymentStatus.objects.bulk_create(
                    [
                        EmploymentStatus(id=1, name="Self"),
                        EmploymentStatus(id=2, name="Salaried"),
                    ]
                )
                message9 = "Successfully Initialised Employment Status"
                print(message9)
            else:
                message9 = "Employment status already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Loan Document Types
        try:
            documents = DocumentTypes.objects.filter()
            if documents.__len__() == 0:
                print("No document types! Initialising document types...")
                DocumentTypes.objects.bulk_create(
                    [
                        DocumentTypes(
                            id=1, name="Photo", category="kyc_document", code="PHT"
                        ),
                        DocumentTypes(
                            id=2, name="ID Card", category="kyc_document", code="ID"
                        ),
                        DocumentTypes(
                            id=3,
                            name="Logbook",
                            category="collateral_document",
                            code="LOG",
                        ),
                        DocumentTypes(
                            id=4,
                            name="Proof of Income",
                            category="application_document",
                            code="POI",
                        ),
                        DocumentTypes(
                            id=5,
                            name="M-Pesa Statement",
                            category="income_statements",
                            code="MPS",
                        ),
                        DocumentTypes(
                            id=6,
                            name="Bank Statement",
                            category="income_statements",
                            code="BST",
                        ),
                        DocumentTypes(
                            id=7,
                            name="Affidavit",
                            category="application_document",
                            code="AFF",
                        ),
                        DocumentTypes(
                            id=8,
                            name="Affordability Calculator",
                            category="application_document",
                            code="AFC",
                        ),
                        DocumentTypes(
                            id=9,
                            name="Bank or ATM card",
                            category="kyc_document",
                            code="BNK",
                        ),
                        DocumentTypes(
                            id=10, name="KRA Pin", category="kyc_document", code="KRA"
                        ),
                        DocumentTypes(
                            id=11,
                            name="Employment Letter",
                            category="kyc_document",
                            code="EMP",
                        ),
                        DocumentTypes(
                            id=12,
                            name="Buyoff Documents",
                            category="application_document",
                            code="BYF",
                        ),
                        DocumentTypes(
                            id=13, name="Payslip", category="kyc_document", code="PYS"
                        ),
                        DocumentTypes(
                            id=14,
                            name="Business Registration or Employment Documents",
                            category="kyc_document",
                            code="BRD",
                        ),
                        DocumentTypes(
                            id=15,
                            name="Proforma Invoice",
                            category="application_document",
                            code="PRI",
                        ),
                        DocumentTypes(
                            id=16,
                            name="Insurance Sticker",
                            category="collateral_document",
                            code="INS",
                        ),
                        DocumentTypes(
                            id=17,
                            name="Credit Life Policy",
                            category="application_document",
                            code="CRLF",
                        ),
                        DocumentTypes(
                            id=18, name="Passport", category="kyc_document", code="PSP"
                        ),
                        DocumentTypes(
                            id=19,
                            name="Work Permit",
                            category="kyc_document",
                            code="WPMT",
                        ),
                        DocumentTypes(
                            id=20,
                            name="Proof of address",
                            category="kyc_document",
                            code="POA",
                        ),
                        DocumentTypes(
                            id=21, name="ID Front", category="kyc_document", code="IDF"
                        ),
                        DocumentTypes(
                            id=22, name="ID Back", category="kyc_document", code="IDB"
                        ),
                        DocumentTypes(
                            id=23,
                            name="Pre Agreement",
                            category="application_document",
                            code="PRA",
                        ),
                        DocumentTypes(
                            id=24,
                            name="Mandate & Debit Order Auth Agreement",
                            category="application_document",
                            code="MDA",
                        ),
                    ]
                )
                message10 = "Successfully Initialised Document Types"
                print(message10)
            else:
                message10 = "Document types already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Leads reason for closing
        try:
            leads_reason = ReasonForClosing.objects.filter()
            if leads_reason.__len__() == 0:
                print(
                    "No leads reason for closing! Initialising leads reason for reason..."
                )
                ReasonForClosing.objects.bulk_create(
                    [
                        ReasonForClosing(id=1, reason="Converted to Sale"),
                        ReasonForClosing(id=2, reason="Got a loan from a competitor"),
                        ReasonForClosing(id=3, reason="No longer interested"),
                    ]
                )
                message11 = "Successfully Initialised Leads reasons for closing"
                print(message11)
            else:
                message11 = "Leads reasons already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Loan Product
        try:
            products = LoanProduct.objects.filter()
            if products.__len__() == 0:
                print("No loan product! Initialising loan products...")
                LoanProduct.objects.bulk_create(
                    [
                        LoanProduct(
                            id=1,
                            name="GOVERNMENT PAYROLL",
                            code="0001",
                            min_amount=10000.00,
                            max_amount=1500000.0000000000,
                            credit_comm_limit=500000.00,
                            default_exception=False,
                        ),
                        LoanProduct(
                            id=2,
                            name="VLB",
                            code="0002",
                            min_amount=50000.00,
                            max_amount=10000000.0000000000,
                            credit_comm_limit=500000.00,
                            default_exception=True,
                        ),
                        LoanProduct(
                            id=3,
                            name="SALARY ADVANCE",
                            code="0003",
                            min_amount=5000.00,
                            max_amount=200000.0000000000,
                            credit_comm_limit=150000.00,
                            default_exception=False,
                        ),
                        LoanProduct(
                            id=4,
                            name="V-CASH",
                            code="0004",
                            min_amount=5000.00,
                            max_amount=1500000.0000000000,
                            credit_comm_limit=0.00,
                            default_exception=False,
                        ),
                        LoanProduct(
                            id=5,
                            name="ASSET FINANCE",
                            code="0005",
                            min_amount=50000.00,
                            max_amount=10000000.0000000000,
                            credit_comm_limit=500000.00,
                            default_exception=True,
                        ),
                        LoanProduct(
                            id=6,
                            name="FIN PAY 50K",
                            code="CL002",
                            min_amount=10001.00,
                            max_amount=50000.0000000000,
                            credit_comm_limit=50000.00,
                            default_exception=False,
                        ),
                        LoanProduct(
                            id=7,
                            name="FIN PAY VLB",
                            code="CL003",
                            min_amount=1.00,
                            max_amount=100000.0000000000,
                            credit_comm_limit=100000.00,
                            default_exception=False,
                        ),
                        LoanProduct(
                            id=10,
                            name="FIN PAY 10K",
                            code="CL001",
                            min_amount=1.00,
                            max_amount=10000.0000000000,
                            credit_comm_limit=10001.00,
                            default_exception=False,
                        ),
                    ]
                )
                message12 = "Successfully Initialised Loan Products"
                print(message12)
            else:
                message12 = "Loan products already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Currency
        try:
            currency = Currency.objects.filter()
            if currency.__len__() == 0:
                print("No loan currency! Initialising loan currency...")
                Currency.objects.bulk_create(
                    [
                        Currency(
                            id=1,
                            name="South African Rand",
                            symbol="ZAR",
                        ),
                        Currency(
                            id=2,
                            name="Kenyan Shilling",
                            symbol="Ksh",
                        ),
                        Currency(
                            id=3,
                            name="United States Dollar",
                            symbol="USD",
                        ),
                    ]
                )
                message13 = "Successfully Initialised Currency"
                print(message13)
            else:
                message13 = "Currency already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Bridge Validation
        try:
            bridge_validation = BridgeValidation.objects.filter()
            if bridge_validation.__len__() == 0:
                print(
                    "No bridge validation rules! Initialising bridge validation rules..."
                )
                BridgeValidation.objects.bulk_create(
                    [
                        BridgeValidation(
                            name="BRV1-EMPLOYER",
                            code="BRV1",
                            description="Employer verification",
                        ),
                        BridgeValidation(
                            name="BANK-AVS", code="AVS", description="Bank validation"
                        ),
                        BridgeValidation(
                            name="BANK STATEMENTS",
                            code="BSTM",
                            description="Bank statement",
                        ),
                        BridgeValidation(
                            name="EXISTING LOANS",
                            code="EXLNS",
                            description="Existing loans",
                        ),
                        BridgeValidation(
                            name="AFFORDABILITY",
                            code="AFFF",
                            description="Affordability",
                        ),
                        BridgeValidation(
                            name="PAY SLIP", code="PSLP", description="Pay slip"
                        ),
                        BridgeValidation(
                            name="ID DOCUMENT", code="ID", description="Id number"
                        ),
                        BridgeValidation(
                            name="DEBICHECK", code="DBCK", description="Debickeck"
                        ),
                        BridgeValidation(
                            name="RE-OFFER", code="REOFR", description="Re offer"
                        ),
                        BridgeValidation(
                            name="PAY DATE", code="PDTE", description="Pay Date "
                        ),
                        BridgeValidation(
                            name="CONTRACT-VOICE CONTRACT",
                            code="CNRT",
                            description="Contract or Voice Contract",
                        ),
                        BridgeValidation(
                            name="CELL NUMBER", code="CNMB", description="Cell number"
                        ),
                        BridgeValidation(
                            name="FRAUDULANT BEHAVIOUR",
                            code="FRBHR",
                            description="Fradulent Behavior",
                        ),
                        BridgeValidation(
                            name="WORK PERMIT", code="WRPT", description="Work permit"
                        ),
                        BridgeValidation(
                            name="CREDIT LIFE", code="CRLF", description="Credit life"
                        ),
                        BridgeValidation(
                            name="CREDIT BUREAU",
                            code="CRB",
                            description="Credit Bureau",
                        ),
                        BridgeValidation(
                            name="FRAUD DETECTION",
                            code="FRD",
                            description="Fraud Detection",
                        ),
                        BridgeValidation(
                            name="ID TYPE", code="IDT", description="Id Type"
                        ),
                        BridgeValidation(
                            name="FIN PAY", code="FNP", description="Fin Pay"
                        ),
                    ]
                )
                message14 = "Successfully Initialised Bridge Validation"
                print(message13)
            else:
                message14 = "Bridge Validation already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Consents
        try:
            consents = ProductConsents.objects.filter()
            if consents.__len__() == 0:
                print("No consents! Initialising product consents...")
                ProductConsents.objects.bulk_create(
                    [
                        ProductConsents(
                            name="Credit bureau",
                            code="C001",
                            description="I consent to Fin enquiring about my credit status with the credit bureau",
                        ),
                        ProductConsents(
                            name="Over indebted",
                            code="C002",
                            description="I am currently over-indebted",
                        ),
                        ProductConsents(
                            name="Debt review",
                            code="C003",
                            description="I am under administration, sequestration or debt review and have not been declared mentally unfit by an order of court",
                        ),
                        ProductConsents(
                            name="Contact marketing",
                            code="C004",
                            description="I consent to be contacted for service feedback and/or information about other products and services.",
                        ),
                        ProductConsents(
                            name="Email correspondence",
                            code="C005",
                            description="I agree to receive correspondence via e-mail and not by post",
                        ),
                        ProductConsents(
                            name="Upfront Initiation fee",
                            code="C006",
                            description="I consent for the upfront initiation fee to be financed with principal debt",
                        ),
                        ProductConsents(
                            name="Credit Life",
                            code="C007",
                            description="To obtain Credit Life Insurance (s44 of the Long-term Insurance Act).",
                        ),
                        ProductConsents(
                            name="Foreign Prominent Public Official",
                            code="C008",
                            description="I confirm that I am a Foreign Prominent Public Official",
                        ),
                        ProductConsents(
                            name="Domestic Prominent Influential person",
                            code="C009",
                            description="I confirm that I am a Domestic Prominent Influential person",
                        ),
                        ProductConsents(
                            name="Terms and Conditions",
                            code="C010",
                            description="I consent to the credit terms and conditions",
                        ),
                        ProductConsents(
                            name="Updates and marketing comms",
                            code="C011",
                            description="I would like to receive updates and marketing communication",
                        ),
                        ProductConsents(
                            name="Use of information conditions",
                            code="C012",
                            description="You provide voluntary, specific and informed consent to the use and disclosure of your personal information, and give Fin and their affiliates permission verify any information we need in connection with this agreement. We share your data with third parties involved in the process of providing the services you request, credit bureaus, customer service providers, lenders and collection agencies. We have trusted relationships with these carefully selected third parties. All service providers are bound by contract to maintain the confidentiality and security of your personal information and are restricted in their use thereof as per our Privacy Policy.",
                        ),
                    ]
                )
                message15 = "Successfully Initialised Product Consents"
                print(message15)
            else:
                message15 = "Product Consents already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Integration
        try:
            integration = Integration.objects.filter()
            if integration.__len__() == 0:
                print("No integrations! Initialising integration...")
                Integration.objects.bulk_create(
                    [
                        Integration(
                            name="BRV1-EMPLOYER",
                            code="BRV1",
                            description="Employer verification",
                        ),
                        Integration(
                            name="SAFPS-FRAUD", code="SAFP", description="SAFPS Fraud"
                        ),
                        Integration(
                            name="INTECON-AVS",
                            code="AVS",
                            description="Bank validation",
                        ),
                        Integration(
                            name="INTECON-DEBICHECK",
                            code="I-DBCK",
                            description="Debickeck Intecon",
                        ),
                        Integration(
                            name="ABSA-DEBICHECK",
                            code="A-DBCK",
                            description="Debickeck Absa",
                        ),
                        Integration(
                            name="REVIO-DEBICHECK",
                            code="R-DBCK",
                            description="Debickeck Revio",
                        ),
                        Integration(
                            name="NUPAY-DEBICHECK",
                            code="N-DBCK",
                            description="Debickeck NuPay",
                        ),
                        Integration(
                            name="STITCH", code="STCH", description="Stitch Payments"
                        ),
                        Integration(name="TRUID", code="TRID", description="TruID"),
                        Integration(
                            name="TRANSUNION-BUREAUE",
                            code="T-CRB",
                            description="Credit Bureaue Transunion",
                        ),
                        Integration(
                            name="EXPERIAN-BUREAUE",
                            code="E-CRB",
                            description="Credit Bureaue Experian",
                        ),
                        Integration(
                            name="VCCB-BUREAUE",
                            code="V-CRB",
                            description="Credit Bureaue VCCB",
                        ),
                        Integration(
                            name="CREDIT LIFE", code="CRLF", description="Credit life"
                        ),
                        Integration(
                            name="CDE-SCRIPT",
                            code="CDE",
                            description="Credit Decision Engine Script",
                        ),
                        Integration(
                            name="BONDSTER-FINANCIER",
                            code="B-FNCR",
                            description="Financier Bondster",
                        ),
                        Integration(
                            name="MINTOS-FINANCIER",
                            code="M-FNCR",
                            description="Financier Mintos",
                        ),
                        Integration(
                            name="FRACTAL-SCORELAB",
                            code="S-FRA",
                            description="Score Lab Affordability Risk Management",
                        ),
                        Integration(
                            name="FRACTAL-TRANSACTIONLAB",
                            code="T-FRA",
                            description="Transaction Lab Affordability Bank Statement analysis",
                        ),
                        Integration(
                            name="CREATE-LOAN-FROM-BACKOFFICE",
                            code="CLB",
                            description="Can create Loan from Backoffice",
                        ),
                        Integration(
                            name="FIN-PAY",
                            code="FNP",
                            description="Has a Fin Pay Product",
                        ),
                        Integration(
                            name="DANGEROUS-OVERRIDE-WARNINGS",
                            code="DOW",
                            description="A loan with validation warnings cannot be sent to disbursement but if this validation is set that can be ignored. Only use this when its necessary and you are very sure.",
                        ),
                        Integration(
                            name="OVERRIDE-AMOUNTS",
                            code="OVAM",
                            description="User can override approved loans amounts, tenure, disbursement",
                        ),
                        Integration(
                            name="CONTRACT",
                            code="CNRT",
                            description="Requires signed contract before disbursement",
                        ),
                    ]
                )
                message16 = "Successfully Initialised Integrations"
                print(message16)
            else:
                message16 = "Integrations already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Comms Templates
        try:
            comms = CommsTemplate.objects.filter()
            if comms.__len__() == 0:
                print("No bridge comss! Initialising comss...")
                CommsTemplate.objects.bulk_create(
                    [
                        CommsTemplate(
                            name="Submited",
                            code="SBT",
                            description="Dear {customer_name}  Congratualtions, you have successfully submitted your loan application of {loan_amount} over {term} months.Here is a copy of your Pre-Agreement {preagreement_url} Queries or progress on your application? Login {service_url} ,Call or WhatsApp us on 0120450606",
                        ),
                        CommsTemplate(
                            name="Pending Documents",
                            code="PND",
                            description="Dear {customer_name} , your application is almost complete. Please send us the following documents to complete your application {document_list}. Email documents@fin.africa or WhatsApp to 0120450606. Use your ID number as a reference.",
                        ),
                        CommsTemplate(
                            name="Declined-Affordability",
                            code="DCA",
                            description="Dear {customer_name} , your application has been declined due to affordability. For more information Login {service_url}, Call or WhatsApp us on 0120450606.",
                        ),
                        CommsTemplate(
                            name="Declined-Credit Criterion",
                            code="DCC",
                            description="Dear {customer_name} , your application has been declined due to failing our credit criterion. For more information please Login {service_url}, Call or WhatsApp us on 0120450606.",
                        ),
                        CommsTemplate(
                            name="Approved",
                            code="APR",
                            description="Welcome {customer_name} to the Fin family, here is confirmation of your approved loan, Loan Amount {loan_amount}, over {tenure} Months, Monthly installment {instalment} starting {starting_date}. For more infomation ~short URL~ . Login {service_url}, call or WhatsApp us on 0120450606.",
                        ),
                        CommsTemplate(
                            name="Delayed",
                            code="DLY",
                            description="Dear {customer_name} , your application is still in progress. We know you are still waiting and havent forgotten you. We will keep you updated each step of the way. For more information please Login {service_url},  call or WhatsApp us on 0120450606.",
                        ),
                        CommsTemplate(
                            name="OTP",
                            code="OPT",
                            description="Contract Signature OTP {otp} {customer_name} your loan {loan_ref}, Loan Amount {loan_amount}, over 6 Months, Monthly installment R2530 starting {starting_date} is ready for authorisation. Please click link  ~short URL~, Login {service_url} or reply YES to this SMS to accept the loan and credit life insurance agreements. Queries? Call or WhatsApp 0120450606.",
                        ),
                        CommsTemplate(
                            name="ReOffer",
                            code="ROF",
                            description="Dear {customer_name}, Important update: Changes to Affordability, Bank, or Employment details may impact previous offerings. Please click the link below to review and accept new terms. Reoffer Link {service_url}. If any questions, call call or WhatsApp us on 0120450606.",
                        ),
                        CommsTemplate(
                            name="Contract",
                            code="CNRT",
                            description="Dear {customer_name}, Important update: Kindly find the attached contract. Please click the link below review and sign the agreement. Contract Link {service_url}. If any questions, call or WhatsApp us on 0120450606.",
                        ),
                    ]
                )
                message17 = "Successfully Initialised comms"
                print(message17)
            else:
                message17 = "Comms already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Dest Accts
        try:
            destination_accounts = DestinationAccount.objects.filter()
            if destination_accounts.__len__() == 0:
                print("No destination! Initialising destination accnts...")
                DestinationAccount.objects.bulk_create(
                    [
                        DestinationAccount(
                            name="Loan Account",
                            code="LNA",
                        ),
                        DestinationAccount(
                            name="Savings Account",
                            code="SNA",
                        ),
                    ]
                )
                message18 = "Successfully Initialised destnation accts"
                print(message18)
            else:
                message18 = "Dest accounts already initialised."
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        # Initialising Custom Permissions

        try:
            permissions = Permission.objects.filter()

            if permissions.__len__() == 0:
                print("No permissions! Initialising permissions...")
                Permission.objects.bulk_create(
                    [
                        Permission(
                            name="Can override bank details",
                            codename="override_bank_details",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can override employer",
                            codename="override_employer",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can change bank details",
                            codename="change_bankdetails",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can change employment details",
                            codename="change_employment_details",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can change client details",
                            codename="change_client_details",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can change debt obligations",
                            codename="change_debt_obligations",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can blacklist clients",
                            codename="can_blacklist_clients",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can view internal loans",
                            codename="view_internal_loans",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can perform admin actions",
                            codename="perform_admin_actions",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can override phone",
                            codename="override_phone",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can override fraud",
                            codename="override_fraud",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can delete documents",
                            codename="delete_documents",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can change affordability",
                            codename="change_affordability",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can offer new product",
                            codename="offer_new_product",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can request credit report",
                            codename="request_credit_report",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can view clients",
                            codename="view_clients",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can view client details",
                            codename="view_client_details",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can view identification info",
                            codename="view_identification_info",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can view client loans",
                            codename="view_client_loans",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can view admin panel",
                            codename="can_view_admin_panel",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can waive charges",
                            codename="waive_charges",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can make repayments",
                            codename="make_repayments",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can settle loans",
                            codename="settle_loans",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                        Permission(
                            name="Can refund",
                            codename="can_refund",
                            content_type=ContentType.objects.get_for_model(Loan),
                        ),
                    ]
                )
        except Exception as e:
            raise CommandError("Something went wrong {}".format(str(e)))

        messagex = f"${message}\n${message2}\n${message3}\n${message4}\n${message5}\n${message6}\n${message7}\n${message8}\n${message9}\n${message10}\n${message11}\n${message12}\n${message13}\n${message14}\n${message15}\n${message16}\n${message17}\n${message18}"
        self.stdout.write(self.style.SUCCESS(messagex))
