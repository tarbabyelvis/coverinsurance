from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context
from loans.models import *
from reports.models import *
from transaction_log.models import TransactionLog
from users.models import Branch, SatelliteBranch,User, Profile
from leads.models import *
from collection.models import SettlementCharges
from clients.models import *
from django.db import connections
import warnings
class Command(BaseCommand):
    help = 'Migrate data from one schema to another'

    def handle(self, *args, **options):
        # Connect to the source (non-multi-tenant) database
        # Connect to the source (non-multi-tenant) database
        source_db_alias = 'default'
        # Connect to the multi-tenanted database
        tenant_db_alias = 'fin_kenya'  # Replace with the actual tenant alias
        tables_list = [\
                    #   "users_branch",\
                    #   "users_satellitebranch",\
                    #   "users_user",\
                    #    "authtoken_token",\
                    #   "loans_loantype",\
                    #   "loans_loanproduct",\
                    #   "loans_teams",\
                    #   "loans_loanstage",\
                    #   "loans_paymentmodes",\
                    #   "loans_typeofbusiness",\
                    #   "loans_employer",\
                    #   "loans_loanpriority",\
                    #    "loans_loan",\
                    #   "loans_employmentstatus",\
                    #   "loans_insurancecompany",\
                    #   "loans_trackingcompany",\
                    #   "loans_assetfianceloan",\
                    #    "loans_callbacksms",\
                    #   "loans_documenttypes",\
                    #   "loans_imsicheck",\
                    #   "loans_loanrejectionreasons",\
                    #    "loans_loanassignment",\
                    #    "loans_loandocuments",\
                    #    "loans_loansecurity",\
                    #    "loans_loanthirdparty",\
                       "loans_loantracker",\
                    #    "loans_lodgingreference",\
                    #    "loans_refinanceaccounts",\
                    #    "loans_servicelevelagreement",\
                    #    "loans_vlbloan",\
                    #   "reports_branchtarget",\
                    #   "reports_monthlytarget",\
                    #    "transaction_log_transactionlog",\
                    #   "users_profile",\
                    #   "leads_reasonforclosing",\
                    #   "leads_clientdetails",\
                    #   "leads_clientleadtracker",\
                    #   "collection_settlementcharges",\
                    #   "clients_bankdetails",\
                    #   "clients_employmentdetails",\
                    #   "clients_nextofkindetails"
                      ]
        
        with connections[source_db_alias].cursor() as source_cursor, \
             connections[tenant_db_alias].cursor() as destination_cursor:
            
            for source_table in tables_list:
                print(f"Migrating source table {source_table}")

                # self.persist_handler_primaryIndex(table=source_table,destination_cursor=destination_cursor)
                self.persist_handler(\
                    table=source_table,source_cursor=source_cursor,\
                    destination_cursor=destination_cursor,destination_tenant=tenant_db_alias)
            
            
        self.stdout.write(self.style.SUCCESS('Data migration complete.'))
    
    def persist_handler(self,table, source_cursor,destination_cursor, destination_tenant):
        # Fetch data from the source table
        # source_cursor.execute(f"SELECT * FROM {table}")
        # source_cursor.execute(f"SELECT * FROM {table} where date(updated_at) >= '2023-11-27' and status=9")
        # source_cursor.execute(f"select * from {table} where date(updated_at) >= '2023-11-27' and stage_id = 9 and status=2")
        source_data = source_cursor.fetchall()

        # Insert data into the destination table
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        # Insert data into the destination table
            columns = ', '.join([f'"{col[0]}"' for col in source_cursor.description])
            print("Columns:")
            print(columns)
            for row in source_data:
                # values = ', '.join([f"'{value}'" for value in row])  # Adjust based on your field types
                # row_values = ', '.join([f"'{value}'" if value is not None else "null" for value in row])
                row_values = [value if value is not None and value != 'None' else None for value in row]
                print("Row values:")
                print(row_values)
                values = ', '.join(['%s' for _ in row])
                print("Values:")
                print(values)
                # destination_cursor.execute(f"INSERT INTO {destination_tenant}.{table}({columns}) VALUES ({values})")
                # query = f"INSERT INTO {destination_tenant}.{table}({columns}) VALUES ({values});"
                query = f"UPDATE {destination_tenant}.{table} set status=2"
                print(f"Query: {query}")
                try:
                    destination_cursor.execute(query, (row_values))
                except Exception as e:
                    print(f"Failed to save: {e}")
                print(f"Finished inserting data into destination table: {table}")
    
    def persist_handler_primaryIndex(self,table,destination_cursor):

        # Insert data into the destination table
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            query = f"SELECT setval('fin_kenya.{table}_id_seq', (SELECT MAX(id) FROM fin_kenya.{table})+1,true);"
            print(f"Query: {query}")
            destination_cursor.execute(query)

       



def migrate_data_between_schemas():
    # Query data from the source schema
    source = 'default'
    destination = 'fin_kenya_prod'
    print("Selecting the required schemas relationships in their order...")
    # branch_data = Branch.objects.using(f'{source}').all()
    # satelite_branch_data = SatelliteBranch.objects.using(f'{source}').all()
    # user_data = User.objects.using(f'{source}').all()
    # loan_type_data = LoanType.objects.using(f'{source}').all()
    # # currency_data = Currency.objects.using(f'{source}').all()
    # # destination_account_data = DestinationAccount.objects.using(f'{source}').all()
    # loan_product_data = LoanProduct.objects.using(f'{source}').all()
    # teams_data = Teams.objects.using(f'{source}').all()
    # loan_stage_data = LoanStage.objects.using(f'{source}').all()
    # payment_mode_data = PaymentModes.objects.using(f'{source}').all()
    # type_of_business_data = TypeOfBusiness.objects.using(f'{source}').all()
    # employer_data = Employer.objects.using(f'{source}').all()
    # loan_priority_data = LoanPriority.objects.using(f'{source}').all()
    # loan_data = Loan.objects.using(f'{source}').all()
    # employment_status_data =EmploymentStatus.objects.using(f'{source}').all()
    # insurance_company_data =InsuranceCompany.objects.using(f'{source}').all()
    # tracking_company_data = TrackingCompany.objects.using(f'{source}').all()
    # loan_asset_finance = AssetFianceLoan.objects.using(f'{source}').all()
    # call_back_sms_data = CallBackSMS.objects.using(f'{source}').all()
    # document_type_data = DocumentTypes.objects.using(f'{source}').all()
    # imsi_check_data = ImsiCheck.objects.using(f'{source}').all()
    # loan_rejection_reason_data = LoanRejectionReasons.objects.using(f'{source}').all()
    # loan_assignement_data = LoanAssignment.objects.using(f'{source}').all()
    # loan_documents_data =LoanDocuments.objects.using(f'{source}').all()
    # loan_security_data = LoanSecurity.objects.using(f'{source}').all()
    # loan_third_party_data = LoanThirdparty.objects.using(f'{source}').all()
    # loan_tracker_data = LoanTracker.objects.using(f'{source}').all()
    # lodging_reference_data = LodgingReference.objects.using(f'{source}').all()
    # refinance_account_data = RefinanceAccounts.objects.using(f'{source}').all()
    # loan_service_level_agreement_data = ServiceLevelAgreement.objects.using(f'{source}').all()
    # vlb_loan_data = VLBLoan.objects.using(f'{source}').all()
    # branch_target_data = BranchTarget.objects.using(f'{source}').all()
    # monthly_target_data = MonthlyTarget.objects.using(f'{source}').all()
    # transaction_log_data = TransactionLog.objects.using(f'{source}').all()
    # profile_data = Profile.objects.using(f'{source}').all()
    # reason_for_closing_data = ReasonForClosing.objects.using(f'{source}').all()
    # client_details_data = ClientDetails.objects.using(f'{source}').all()
    # client_lead_tracker_data = ClientLeadTracker.objects.using(f'{source}').all()
    # settlement_charges_data = SettlementCharges.objects.using(f'{source}').all()
    # bank_details_data = BankDetails.objects.using(f'{source}').all()
    # employment_details_data =EmploymentDetails.objects.using(f'{source}').all()
    # next_kin_details_data = NextOfKinDetails.objects.using(f'{source}').all()

    # # Weird behavior but thats how it is i guess, Init the hashed object
    # for item in branch_data:
    #     print(f"Migrating branch: {item}")
    # for item in satelite_branch_data:
    #         print(f"Migrating satelite: {item}")
    # for item in user_data:
    #         print(f"Migrating user: {item}")
    # for item in loan_type_data:
    #         print(f"Migrating loantype: {item}")
    # # for item in currency_data:
    # #         print(f"Migrating currency: {item}")
    # for item in loan_product_data:
    #         print(f"Migrating product: {item}")
    # # for item in destination_account_data:
    # #         print(f"Migrating destination account: {item}")
    # for item in teams_data:
    #         print(f"Migrating teams: {item}")
    # for item in loan_stage_data:
    #         print(f"Migrating stage: {item}")
    # for item in payment_mode_data:
    #         print(f"Migrating mode: {item}")
    # for item in type_of_business_data:
    #         print(f"Migrating business: {item}")
    # for item in employer_data:
    #         print(f"Migrating employer: {item}")
    # for item in loan_priority_data:
    #         print(f"Migrating priority: {item}")
    # for item in loan_data:
    #         print(f"Migrating loan: {item}")
    # for item in employment_status_data:
    #         print(f"Migrating employmentstatus: {item}")
    # for item in insurance_company_data:
    #         print(f"Migrating insruance: {item}")
    # for item in tracking_company_data:
    #         print(f"Migrating tracking: {item}")
    # for item in loan_asset_finance:
    #         print(f"Migrating asset: {item}")
    # for item in call_back_sms_data:
    #         print(f"Migrating callback: {item}")
    # for item in document_type_data:
    #         print(f"Migrating document: {item}")
    # for item in imsi_check_data:
    #         print(f"Migrating imsi: {item}")
    # for item in loan_rejection_reason_data:
    #         print(f"Migrating rejection: {item}")
    # for item in loan_assignement_data:
    #         print("Migrating assignemnt:")
    # for item in loan_documents_data:
    #         print("Migrating document")
    # for item in loan_security_data:
    #     print(f"Migrating security: {item}") 
    # for item in loan_third_party_data:
    #     print(f"Migrating thirdparty: {item}")
    # for item in loan_tracker_data:
    #     print("Migrating tracker:")
    # for item in lodging_reference_data:
    #     print(f"Migrating reference: {item}")
    # for item in refinance_account_data:
    #     print(f"Migrating refinance: {item}")
    # for item in loan_service_level_agreement_data:
    #     print(f"Migrating sla: {item}")
    # for item in vlb_loan_data:
    #     print(f"Migrating vlb: {item}")
    # for item in branch_target_data:
    #     print(f"Migrating branch: {item}")
    # for item in monthly_target_data:
    #     print(f"Migrating montly: {item}")
    # for item in transaction_log_data:
    #     print(f"Migrating transaction: {item}")
    # for item in profile_data:
    #     print("Migrating profile:")
    # for item in reason_for_closing_data:
    #     print(f"Migrating reason: {item}")
    # for item in client_details_data:
    #     print(f"Migrating client: {item}")
    # for item in client_lead_tracker_data:
    #     print(f"Migrating lead tracker: {item}")
    # for item in settlement_charges_data:
    #     print(f"Migrating settlement: {item}")
    # for item in bank_details_data:
    #     print(f"Migrating bank: {item}")
    # for item in employment_details_data:
    #     print(f"Migrating employment: {item}")
    # for item in next_kin_details_data:
    #     print(f"Migrating next: {item}")
    # Migrate data to the destination schema

    # with schema_context(f"{destination}"):
    #     print("Now in schemas context")
    #     for item in branch_data:
    #         print(f"Migrating branch: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in satelite_branch_data:
    #         print(f"Migrating satelite: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
    #     try:
    #         for item in user_data:
    #             print(f"Migrating user: {item}")
    #             item.save()
    #             print(f"Finished saving: {item}")
    #     except Exception as e:
    #         print(f"Something went wrong {e}")

    #     for item in loan_type_data:
    #         print(f"Migrating loantype: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     # for item in currency_data:
    #     #     print(f"Migrating currency: {item}")
    #     #     item.save()
    #     #     print(f"Finished saving: {item}")
        
    #     # for item in destination_account_data:
    #     #     print(f"Migrating destination account: {item}")
    #     #     item.save()
    #     #     print(f"Finished saving: {item}")

    #     for item in loan_product_data:
    #         print(f"Migrating loanproduct: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in teams_data:
    #         print(f"Migrating teams: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_stage_data:
    #         print(f"Migrating stage: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in payment_mode_data:
    #         print(f"Migrating payment: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in type_of_business_data:
    #         print(f"Migrating business: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in employer_data:
    #         print(f"Migrating employer: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_priority_data:
    #         print(f"Migrating priority: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     # Migrating the loans ....
    #     for item in loan_data:
    #         print(f"Migrating loan: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in employment_status_data:
    #         print(f"Migrating emplstatus: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in insurance_company_data:
    #         print(f"Migrating insurance: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in tracking_company_data:
    #         print(f"Migrating tracking company: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_asset_finance:
    #         print(f"Migrating assetfinance: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in call_back_sms_data:
    #         print(f"Migrating callback: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in document_type_data:
    #         print(f"Migrating documenttype: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in imsi_check_data:
    #         print(f"Migrating imsi: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in loan_rejection_reason_data:
    #         print(f"Migrating rejection: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in loan_assignement_data:
    #         print("Migrating assignemnt:")
    #         item.save()
    #         print(f"Finished saving:")
        
    #     for item in loan_documents_data:
    #         print(f"Migrating document: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_security_data:
    #         print(f"Migrating security: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_third_party_data:
    #         print(f"Migrating thirdpart: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_tracker_data:
    #         print(f"Migrating tracker: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in lodging_reference_data:
    #         print(f"Migrating lodging reference: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in refinance_account_data:
    #         print(f"Migrating lodging refinance: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in loan_service_level_agreement_data:
    #         print(f"Migrating lodging sla: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in vlb_loan_data:
    #         print(f"Migrating lodging vlb: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in branch_target_data:
    #         print(f"Migrating lodging branch: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in monthly_target_data:
    #         print(f"Migrating lodging monthly: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in transaction_log_data:
    #         print(f"Migrating lodging transactionlog: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     for item in profile_data:
    #         print(f"Migrating lodging profile: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in reason_for_closing_data:
    #         print(f"Migrating reason: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in client_details_data:
    #         print(f"Migrating leads: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in client_lead_tracker_data:
    #         print(f"Migrating lead tracker: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in settlement_charges_data:
    #         print(f"Migrating settlement: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in next_kin_details_data:
    #         print(f"Migrating next: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in employment_details_data:
    #         print(f"Migrating employment: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")
        
    #     for item in next_kin_details_data:
    #         print(f"Migrating next: {item}")
    #         item.save()
    #         print(f"Finished saving: {item}")

    #     # for item in source_data:
    #     #     print("Migrating data:")
    #     #     print(item)
    #     #     # Modify data or perform any necessary transformations
    #     #     # Save the item to the destination schema
    #     #     item.save()