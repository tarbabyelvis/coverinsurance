import traceback
from datetime import datetime, date

from claims.models import Claim
from claims.serializers import ClaimSerializer
from config.enums import PolicyType
from config.models import ClaimantDetails
from core.utils import first_day_of_previous_month, last_day_of_previous_month
from integrations.enums import Integrations
from integrations.guardrisk.guardrisk import GuardRisk
from integrations.models import IntegrationConfigs
from integrations.superbase import query_new_loans, query_repayments, query_closed_loans, query_written_off_loans
from jobs.models import TaskLog
from policies.models import Policy
from policies.serializers import PolicyDetailSerializer, PremiumPaymentSerializer, \
    ClientPolicyRequestSerializer
from .models import Task

first_day_of_previous_month: date = first_day_of_previous_month().date()
last_day_of_previous_month: date = last_day_of_previous_month().date()
today_start_date: date = datetime.today().date()
today_end_date: date = datetime.today().date()


def daily_job_postings(start_date=today_start_date, end_date=today_end_date):
    print("Running daily job postings")
    nifty_configs = fetch_configs(identifier='Nifty Cover')
    indlu_configs = fetch_configs(identifier='Indlu')
    start_date_time, end_date_time = __get_start_and_end_dates_with_time(start_date, end_date)
    print(f'start date: {start_date_time}, end date: {end_date_time}')
    credit_life_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.CREDIT_LIFE)
    funeral_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.FUNERAL_COVER)
    fetched_claims = __fetch_claims(start_date_time, end_date_time)
    try:
        credit_life_daily(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life cover: {e}")

    try:
        life_funeral_daily(funeral_policies, nifty_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life funeral: {e}")

    try:
        claims_daily(fetched_claims, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending claims: {e}")

    status = 200
    data = {
        "message": "Successfully sent daily job postings",
    }
    return status, data


def monthly_job_postings(start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    """

    @param start_date:
    @type end_date: date
    """
    print("Running monthly job postings")
    nifty_configs = fetch_configs(identifier='Nifty Cover')
    indlu_configs = fetch_configs(identifier='Indlu')
    start_date_time, end_date_time = __get_start_and_end_dates_with_time(start_date, end_date)
    print(f'start date: {start_date_time}, end date: {end_date_time}')
    credit_life_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.CREDIT_LIFE)
    funeral_policies = __fetch_policies(start_date_time, end_date_time, PolicyType.FUNERAL_COVER)
    fetched_claims = __fetch_claims(start_date_time, end_date_time)
    try:
        credit_life_monthly(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending monthly job: {e}")

    try:
        life_funeral_monthly(funeral_policies, nifty_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending life funeral: {e}")

    try:
        claims_monthly(fetched_claims, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending monthly claims: {e}")

    status = 200
    data = {
        "message": "Successfully sent monthly job postings",
    }
    return status, data


def __get_start_and_end_dates_with_time(start_date, end_date):
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    return start_datetime, end_datetime


def credit_life_daily(credit_life_policies, nifty_configs, indlu_configs, start_date=today_start_date,
                      end_date=today_end_date):
    __credit_life(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)


def credit_life_monthly(credit_life_policies, nifty_configs, indlu_configs,
                        start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    __credit_life(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date, False)


def __credit_life(
        credit_life_policies, nifty_configs, indlu_configs, start_date, end_date, is_daily_submission=True,
):
    try:
        if credit_life_policies.exists():
            # fetch the data
            nifty_data = list(filter(lambda policy: policy.entity == 'Nifty Cover', credit_life_policies))
            indlu_data = list(filter(lambda policy: policy.entity == 'Indlu', credit_life_policies))

            nifty_policies = PolicyDetailSerializer(nifty_data, many=True).data
            indlu_policies = PolicyDetailSerializer(indlu_data, many=True).data
            print(f'now processing for nifty , {len(nifty_policies)} policies')
            process_credit_life(nifty_policies, nifty_configs, start_date, end_date, is_daily_submission)
            print(f'now processing for indlu , {len(indlu_policies)} policies')
            process_credit_life(indlu_policies, indlu_configs, start_date, end_date, is_daily_submission)
            return
        print('No Life policies to process...')
    except Exception as e:
        print(e)
        raise Exception(e)


def process_credit_life(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('CREDIT_LIFE_DAILY' if is_daily_submission else 'CREDIT_LIFE_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        data, response_status = guard_risk.life_credit_daily(data, start_date, end_date, client_identifier) \
            if is_daily_submission else guard_risk.life_credit_monthly(data, start_date, end_date, client_identifier)
        print(response_status)
        log.data = data
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def life_funeral_daily(funeral_policies, nifty_configs, start_date=today_start_date, end_date=today_end_date):
    __life_funeral(funeral_policies, nifty_configs, start_date, end_date)


def life_funeral_monthly(funeral_policies, nifty_configs, start_date, end_date):
    __life_funeral(funeral_policies, nifty_configs, start_date, end_date, False)


def __life_funeral(
        funeral_policies, nifty_configs, start_date, end_date, is_daily_submission=True
):
    try:
        if funeral_policies.exists():
            nifty_data = list(filter(lambda p: p.entity == 'Nifty Cover', funeral_policies))
            nifty_policies = PolicyDetailSerializer(nifty_data, many=True).data
            process_life_funeral(nifty_policies, nifty_configs, start_date, end_date, is_daily_submission)
        else:
            print('No funeral policies to process...')
    except Exception as e:
        print(e)
        raise Exception(e)


def process_life_funeral(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('LIFE_FUNERAL_DAILY' if is_daily_submission else 'LIFE_FUNERAL_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        data, response_status = guard_risk.life_funeral_daily(data, start_date, end_date, client_identifier) \
            if is_daily_submission else guard_risk.life_funeral_monthly(data, start_date, end_date, client_identifier)
        print(response_status)
        log.data = data
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        traceback.print_exc()
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def claims_daily(claims_fetched, nifty_configs, indlu_configs, start_date=today_start_date, end_date=today_end_date):
    return __claims(claims_fetched, nifty_configs, indlu_configs, start_date, end_date)


def claims_monthly(claims_fetched, nifty_configs, indlu_configs, start_date=first_day_of_previous_month,
                   end_date=last_day_of_previous_month):
    return __claims(claims_fetched, nifty_configs, indlu_configs, start_date, end_date, False)


def __claims(
        fetched_claims, nifty_configs, indlu_configs, start_date, end_date, is_daily_submission=True
):
    try:
        if fetched_claims.exists():
            nifty_data = list(filter(lambda claim: claim.policy.entity == 'Nifty Cover', fetched_claims))
            indlu_data = list(filter(lambda claim: claim.policy.entity == 'Indlu', fetched_claims))

            nifty_claims = ClaimSerializer(nifty_data, many=True).data
            indlu_claims = ClaimSerializer(indlu_data, many=True).data

            process_claims(nifty_claims, nifty_configs, start_date, end_date, is_daily_submission)
            process_claims(indlu_claims, indlu_configs, start_date, end_date, is_daily_submission)
        else:
            print('No claims to process...')
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception(e)


def process_claims(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('CLAIM_DAILY' if is_daily_submission else 'CLAIM_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        client_identifier = integration_configs.client_identifier
        data, response_status = guard_risk.life_claims_daily(data, start_date, end_date, client_identifier) \
            if is_daily_submission else guard_risk.life_claims_monthly(data, start_date, end_date, client_identifier)
        print(response_status)
        log.data = data
        if str(response_status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        traceback.print_exc()
        log.status = "failed"
        log.save()
        raise Exception(e)

    return data, response_status


def fetch_tasks(identifier):
    return Task.objects.filter(task=identifier).first()


def fetch_configs(identifier):
    return IntegrationConfigs.objects.get(
        name=Integrations.GUARDRISK.name, is_enabled=True, entity=identifier
    )


def create_task_logs(task: Task):
    return TaskLog.objects.create(task=task, status="running", manual_run=True)


def __fetch_policies(start_date: datetime, end_date: datetime, policy_type: PolicyType):
    return Policy.objects.filter(
        created__gte=start_date,
        created__lte=end_date,
        policy_type__policy_type=policy_type.name,
        policy_type__isnull=False
    )


def __fetch_claims(start_date: datetime, end_date: datetime):
    return Claim.objects.filter(
        created__gte=start_date,
        created__lte=end_date,
    )


def fetch_and_process_fin_connect_data(start_date: date, end_date: date, fineract_org_id):
    failed_loans = fetch_and_save_new_loans(start_date, end_date, fineract_org_id)
    failed_repayments = fetch_and_save_repayments(start_date, end_date, fineract_org_id)
    failed_closed_loans = fetch_and_update_closed_loans(start_date, end_date, fineract_org_id)
    failed_claims = fetch_and_written_off_loans(start_date, end_date, fineract_org_id)
    print(f'failed_loans:: {len(failed_loans)}')
    print(f'failed_loans data:: {failed_loans}')
    print(f'failed_repayments:: {len(failed_repayments)}')
    print(f'failed_repayments data:: {failed_repayments}')
    print(f'failed_closed_loans:: {len(failed_closed_loans)}')
    print(f'failed_closed_loans:: {failed_closed_loans}')
    print(f'failed_claims:: {len(failed_claims)}')
    print(f'failed_claims:: {failed_claims}')


def fetch_and_update_closed_loans(start_date: date, end_date: date, tenant):
    closed_loans = __fetch_closed_loans_from_fin_connect(start_date, end_date, tenant)
    unexisting = []
    db_policies = []
    for loan in closed_loans:
        try:
            if not loan["loanId"]:
                print(f"Policy ID missing from request! : {loan}")
                unexisting.append(loan['loanId'])
            else:
                policy = Policy.objects.filter(policy_number=loan["loanId"]).first()
                if policy is not None:
                    policy.policy_status = map_closure_reason(loan["closed_reason"])
                    policy.expiry_date = loan["closed_date"]
                    db_policies.append(policy)
        except Exception as e:
            print(f"Error saving {loan['loanId']}")
            print(e)
            unexisting.append(loan['loanId'])
    Policy.objects.bulk_update(db_policies, fields=['policy_status', 'expiry_date'])
    return unexisting


def map_closure_reason(closed_reason: str) -> str:
    if closed_reason == 'Withdrawn by client':
        return "X"
    elif closed_reason == 'Closed' or closed_reason == 'Overpaid':
        return "P"
    else:
        return "P"


def fetch_and_save_new_loans(start_date: date, end_date: date, tenant_id):
    new_loans = __fetch_new_policies_from_fin_connect(start_date, end_date, tenant_id)
    failed_loans = []
    for loan in new_loans:
        try:
            if not loan["loanId"]:
                print(f"Policy ID missing from request! : {loan}")
                failed_loans.append(loan['loanId'])
            else:
                policy, client = extract_policy_and_client_info(loan)
                serializer = ClientPolicyRequestSerializer(
                    data={"client": client, "policy": policy},
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except Exception as e:
            print(f"Error saving {loan['loanId']}")
            print(e)
            failed_loans.append(loan['loanId'])
    return failed_loans


def extract_policy_and_client_info(loan):
    premium = float(loan["premium"])
    policy = {
        "policy_type": 1,
        "insurer": 1,
        "policy_number": loan["loanId"],
        "external_id": loan["loan_external_id"],
        "sum_insured": round(float(loan["loan_amount"]), 2),
        "total_premium": round(float(loan["premium"]), 2),
        "commencement_date": loan["disbursementDate"],
        "policy_status": "A",
        "expiry_date": loan["maturityDate"],
        "product_name": loan["productName"],
        "policy_term": loan["tenure"],
        "admin_fee": calculate_guard_risk_admin_amount(premium),
        "commission_amount": calculate_commission_amount(premium),
        "commission_percentage": 7.50,
        "sub_scheme": "Credit Life",
        "entity": "Indlu",
        "premium_frequency": "Monthly",
        "commission_frequency": "Monthly",
        "policy_details": {
            "binder_fees": calculate_binder_fees_amount(premium),
        }
    }
    client = {
        "client_id": loan["client_primary_id_number"],
        "first_name": loan["client_firstname"],
        "middle_name": loan["client_middlename"],
        "last_name": loan["client_surname"],
        "date_of_birth": loan["dob"],
        "primary_id_number": loan["client_primary_id_number"],
        "primary_id_document_type": 1,
        "gender": loan["client_gender"],
        "marital_status": "Unknown",
        "email": loan["email"],
        "phone_number": loan["mobile_number"],
        "entity_type": "Individual",
    }
    return policy, client


def calculate_commission_amount(premium_amount) -> float:
    return round(0.075 * premium_amount, 2)


def calculate_guard_risk_admin_amount(premium_amount) -> float:
    return round(0.05 * premium_amount, 2)


def calculate_binder_fees_amount(premium_amount) -> float:
    return round(0.09 * premium_amount, 2)


def fetch_and_save_repayments(start_date: date, end_date: date, tenant_id):
    repayments = __fetch_loan_repayments_from_fin_connect(start_date, end_date, tenant_id)
    failed_repayments = []
    for repayment in repayments:
        try:
            if not repayment["loanId"]:
                failed_repayments.append(repayment['loanId'])
            else:
                repayment_details = extract_repayment_details(repayment)
                serializer = PremiumPaymentSerializer(
                    data=repayment_details
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except Exception as e:
            print(f"Error saving {repayment['loanId']}")
            print(e)
            failed_repayments.append(repayment['loanId'])
    return failed_repayments


def extract_repayment_details(repayment):
    return {
        "policy_id": repayment["loanId"],
        "payment_date": repayment["transactionDate"],
        "amount": round(float(repayment["paidAmount"]), 2),
        "transaction_type": repayment["paymentType"],
        "payment_method": repayment["paymentType"],
    }


def __fetch_new_policies_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching new loans")
    new_loans = []
    try:
        response_status, data = query_new_loans(tenant_id, start_date, end_date)
        print(f'response_status: {response_status}:: data: {data}')
        return data
    except Exception as e:
        print("Something went wrong fetching new loans")
        print(e)
        return new_loans


def __fetch_loan_repayments_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching loan repayments")
    collections = []
    try:
        response_status, data = query_repayments(tenant_id, start_date, end_date)
        print(f'response_status: {response_status}:: data: {data}')
        return data
    except Exception as e:
        print("Something went wrong fetching loan repayments")
        print(e)
        return collections


def __fetch_closed_loans_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching closed loans")
    collections = []
    try:
        response_status, data = query_closed_loans(tenant_id, start_date, end_date)
        print(f'response_status: {response_status}:: data: {data}')
        return data
    except Exception as e:
        print("Something went wrong fetching closed loans")
        print(e)
        return collections


def fetch_and_written_off_loans(start_date: date, end_date: date, tenant):
    written_off_loans = __fetch_written_off_policies_from_fin_connect(start_date, end_date, tenant)
    fin_claimant_details = ClaimantDetails.objects.filter(name="Fin").first()
    if fin_claimant_details is None:
        raise Exception("No Fin claimant details found")
    claims = []
    for loan in written_off_loans:
        try:
            claim = create_claim(loan, fin_claimant_details)
            claims.append(claim)
        except Exception as e:
            print(f"Error creating claim for {loan['loanId']}")
            print(e)

    try:
        serializer = ClaimSerializer(
            data=claims, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except Exception as e:
        print(f"Error saving claims")
    return claims


def __fetch_written_off_policies_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching written off loans")
    written_off_loans = []
    try:
        response_status, data = query_written_off_loans(tenant_id, start_date, end_date)
        print(f'response_status: {response_status}:: data: {data}')
        return data
    except Exception as e:
        print("Something went wrong fetching written loans")
        print(e)
        return written_off_loans


def create_claim(written_off_loan, fin_claimant_details):
    policy = Policy.objects.filter(policy_number=written_off_loan["loanId"]).first()
    if policy:
        claim = {
            "policy_id": policy.policy_id,
            "claim_type_id": 1,
            "claim_status": "Active",
            "claimant_name": fin_claimant_details["name"],
            "claimant_surname": fin_claimant_details["surname"],
            "claimant_id_number": fin_claimant_details["id_number"],
            "claimant_id_type": 1,
            "claimant_email": fin_claimant_details["email"],
            "claimant_phone": fin_claimant_details["phone_number"],
            "claimant_bank_name": fin_claimant_details["bank"],
            "claimant_bank_account_number": fin_claimant_details["bank_account_number"],
            "claimant_branch": fin_claimant_details["branch"],
            "claimant_branch_code": fin_claimant_details["branch_code"],
            "claim_assessed_by": "",
            "claim_assessment_date": "",
            "claim_amount": written_off_loan["written_off_amount"],
            "claim_details": {},
            "submitted_date": written_off_loan["written_off_date"],
            "claim_paid_date": "",
        }
        return claim
