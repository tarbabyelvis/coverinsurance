import traceback
from datetime import datetime, date

from django.db.models import Q

from claims.models import Claim
from claims.serializers import ClaimSerializer
from config.enums import PolicyType
from config.models import ClaimantDetails, LoanProduct
from core.utils import first_day_of_previous_month, last_day_of_previous_month, get_loan_id_from_legacy_loan
from integrations.enums import Integrations
from integrations.guardrisk.guardrisk import GuardRisk
from integrations.models import IntegrationConfigs
from integrations.superbase import query_new_loans, query_repayments, query_closed_loans, query_written_off_loans
from integrations.utils import calculate_binder_fees_amount, calculate_commission_amount, \
    calculate_guard_risk_admin_amount
from jobs.models import TaskLog
from policies.models import Policy, PremiumPayment
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
    fetched_premiums = __fetch_premiums(start_date_time, end_date_time)
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

    try:
        premiums_daily(fetched_premiums, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending premiums: {e}")

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
    fetched_premiums = __fetch_premiums(start_date_time, end_date_time)
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

    try:
        premiums_monthly(fetched_premiums, nifty_configs, indlu_configs, start_date, end_date)
    except Exception as e:
        print(f"Error on sending monthly premiums: {e}")

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
    return __credit_life(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date)


def credit_life_monthly(credit_life_policies, nifty_configs, indlu_configs,
                        start_date=first_day_of_previous_month, end_date=last_day_of_previous_month):
    return __credit_life(credit_life_policies, nifty_configs, indlu_configs, start_date, end_date, False)


def __credit_life(
        credit_life_policies, nifty_configs, indlu_configs, start_date, end_date, is_daily_submission=True,
):
    try:
        if credit_life_policies.exists():
            # fetch the data
            nifty_data = list(filter(lambda policy: policy.entity == 'Nifty Cover', credit_life_policies))
            indlu_data = list(filter(lambda policy: policy.entity == 'Indlu', credit_life_policies))
            # indlu_data = [policy for policy in credit_life_policies if policy not in nifty_data]

            nifty_policies = PolicyDetailSerializer(nifty_data, many=True).data
            indlu_policies = PolicyDetailSerializer(indlu_data, many=True).data
            print(f'now processing for nifty , {len(nifty_policies)} policies')
            # _, status = process_credit_life(nifty_policies, nifty_configs, start_date, end_date, is_daily_submission)
            print(f'now processing for indlu , {len(indlu_policies)} policies')
            _, status = process_credit_life(indlu_policies, indlu_configs, start_date, end_date, is_daily_submission)
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
            pass
            # nifty_data = list(filter(lambda p: p.entity == 'Nifty Cover', funeral_policies))
            # nifty_policies = PolicyDetailSerializer(nifty_data, many=True).data
            # process_life_funeral(nifty_policies, nifty_configs, start_date, end_date, is_daily_submission)
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

            # process_claims(nifty_claims, nifty_configs, start_date, end_date, is_daily_submission)
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


def premiums_daily(premiums_fetched, nifty_configs, indlu_configs, start_date=today_start_date,
                   end_date=today_end_date):
    return __premiums(premiums_fetched, nifty_configs, indlu_configs, start_date, end_date)


def premiums_monthly(premiums_fetched, nifty_configs, indlu_configs, start_date=first_day_of_previous_month,
                     end_date=last_day_of_previous_month):
    return __premiums(premiums_fetched, nifty_configs, indlu_configs, start_date, end_date, False)


def __premiums(
        fetched_premiums, nifty_configs, indlu_configs, start_date, end_date, is_daily_submission=True
):
    try:
        if fetched_premiums.exists():
            nifty_data = list(filter(lambda premium: premium.policy.entity == 'Nifty Cover', fetched_premiums))
            indlu_data = list(filter(lambda premium: premium.policy.entity == 'Indlu', fetched_premiums))

            nifty_claims = PremiumPaymentSerializer(nifty_data, many=True).data
            indlu_claims = PremiumPaymentSerializer(indlu_data, many=True).data

            # process_premiums(nifty_claims, nifty_configs, start_date, end_date, is_daily_submission)
            process_premiums(indlu_claims, indlu_configs, start_date, end_date, is_daily_submission)
        else:
            print('No premiums to process...')
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception(e)


def process_premiums(data, integration_configs, start_date, end_date, is_daily_submission=True):
    task = fetch_tasks('PREMIUM_DAILY' if is_daily_submission else 'PREMIUM_MONTHLY')
    log = create_task_logs(task)
    try:
        guard_risk = GuardRisk(integration_configs.access_key, integration_configs.base_url)
        data, response_status = guard_risk.life_premiums_daily(data, start_date, end_date) \
            if is_daily_submission else guard_risk.life_premiums_monthly(data, start_date, end_date)
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
        Q(policy_status='A', policy_type__policy_type=policy_type.name, policy_provider_type='Internal Credit Life',
          commencement_date__range=(start_date, end_date)) |
        Q(policy_status__in=('P', 'C'), policy_type__policy_type=policy_type.name,
          policy_provider_type='Internal Credit Life',
          closed_date__range=(start_date, end_date))
    )


def __fetch_claims(start_date: datetime, end_date: datetime):
    return Claim.objects.filter(
        submitted_date__gte=start_date,
        submitted_date__lte=end_date,
        policy__policy_provider_type='Internal Credit Life'
    )


def __fetch_premiums(start_date: datetime, end_date: datetime):
    return PremiumPayment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        policy__policy_provider_type='Internal Credit Life'
    )


def fetch_and_process_fin_connect_data(start_date: date, end_date: date, fineract_org_id):
    process_new_loans(start_date, end_date, fineract_org_id)
    process_repayments(start_date, end_date, fineract_org_id)
    process_closed_loans(start_date, end_date, fineract_org_id)
    process_claims_from_fineract(start_date, end_date, fineract_org_id)
    print(f'Done processing fineract data fetch for {start_date} to {end_date} and tenant {fineract_org_id}')


def process_new_loans(start_date: date, end_date: date, fineract_org_id):
    new_loans = __fetch_new_policies_from_fin_connect(start_date, end_date, fineract_org_id)
    save_new_loans(new_loans)


def process_repayments(start_date: date, end_date: date, fineract_org_id):
    repayments = __fetch_loan_repayments_from_fin_connect(start_date, end_date, fineract_org_id)
    save_repayments(repayments)
    print(f'Done saving repayments for {start_date} to {end_date}')


def process_closed_loans(start_date: date, end_date: date, fineract_org_id):
    closed_loans = __fetch_closed_loans_from_fin_connect(start_date, end_date, fineract_org_id)
    update_closed_loans(closed_loans)


def process_claims_from_fineract(start_date: date, end_date: date, fineract_org_id):
    written_off_polices = __fetch_written_off_policies_from_fin_connect(start_date, end_date, fineract_org_id)
    create_claims_for_written_off_loans(written_off_polices)


def update_closed_loans(closed_loans):
    db_policies = []
    for loan in closed_loans:
        product_id = loan.get("product_id")
        if is_legacy_policy(product_id):
            policy_number = get_loan_id_from_legacy_loan(loan.get("loan_external_id"))
        else:
            policy_number = loan["loanId"]
        try:
            policy = Policy.objects.filter(policy_number=policy_number).first()
            if policy is None:
                create_policy(loan)
            else:
                create_policy(loan=loan, is_update=True, old_policy=policy)
            policy.policy_status = map_closure_reason(loan["closed_reason"])
            policy.closed_date = loan["closed_date"]
            policy_details = policy.policy_details or {}
            policy_details['current_outstanding_balance'] = float(loan["current_outstanding_balance"])
            policy_details['total_policy_premium_collected'] = float(loan["total_policy_premium_collected"])
            policy.policy_details = policy_details
            db_policies.append(policy)
        except Exception as e:
            print(f"Error updating closed loan  {loan}")
            print(e)
    Policy.objects.bulk_update(db_policies, fields=['policy_status', 'expiry_date', 'policy_details'])


def map_closure_reason(closed_reason: str) -> str:
    if closed_reason == 'Withdrawn by client':
        return "X"
    elif closed_reason == 'Closed' or closed_reason == 'Overpaid':
        return "P"
    else:
        return "P"


def save_new_loans(new_loans):
    failed_loans = []
    for loan in new_loans:
        try:
            create_policy(loan)
        except Exception as e:
            print(f"Error saving new loan{loan['loanId']}")
            print(e)
            failed_loans.append(loan['loanId'])
    return failed_loans


def extract_policy_and_client_info(loan):
    product_id = loan.get("product_id")
    if is_legacy_policy(product_id):
        policy_number = get_loan_id_from_legacy_loan(loan.get("loan_external_id"))
        external_reference = None
    else:
        policy_number = loan["loanId"]
        external_reference = loan.get("loan_external_id", "")
    premium = round(float(loan.get("premium") or 0), 2)
    policy = {
        "policy_type": 1,
        "insurer": 1,
        "policy_number": policy_number,
        "external_reference": external_reference,
        "sum_insured": round(float(loan.get("loan_amount") or 0), 2),
        "total_premium": premium,
        "commencement_date": loan.get("disbursementDate") or date.today().strftime("%Y-%m-%d"),
        "policy_status": "A",
        "expiry_date": loan.get("maturityDate") or date.today().strftime("%Y-%m-%d"),
        "product_name": loan["productName"],
        "policy_term": loan["tenure"],
        "admin_fee": calculate_guard_risk_admin_amount(premium),
        "commission_amount": calculate_commission_amount(premium),
        "commission_percentage": 7.50,
        "premium_frequency": "Monthly",
        "commission_frequency": "Monthly",
        "policy_provider_type": loan["policy_type"],
        "business_unit": loan.get("business_unit", ""),
        "entity": loan.get("entity") or "",
        "is_legacy": loan.get("is_legacy") or False,
        "sub_scheme": loan.get("sub_scheme") or "",
        "policy_type_id": loan.get("policy_type_id", ""),
        "policy_details": {
            "binder_fees": calculate_binder_fees_amount(premium),
            "total_loan_schedule": loan.get("total_loan_schedule") or "0",
            "total_policy_premium_collected": loan.get("total_policy_premium_collected"),
            "current_outstanding_balance": loan.get("current_outstanding_balance") or 0,
            "installment_amount": loan.get("instalment_amount") or 0,
        }
    }
    client = {
        "client_id": loan["client_primary_id_number"],
        "first_name": loan.get("client_firstname", ""),
        "middle_name": loan.get("client_middlename", ""),
        "last_name": loan.get("client_surname", ""),
        "date_of_birth": loan.get("dob", ""),
        "primary_id_number": loan["client_primary_id_number"],
        "primary_id_document_type": 1,
        "gender": loan.get("client_gender") or "Unknown",
        "marital_status": "Unknown",
        "email": loan.get("email", ""),
        "phone_number": loan.get("mobile_number", ""),
        "entity_type": "Individual",
    }
    return policy, client


def create_policy(loan, is_update: bool = False, old_policy=None):
    product_id = int(loan.get("product_id"))
    loan_product = LoanProduct.objects.filter(product_id=product_id).first()
    if loan_product is not None:
        business_unit = loan_product.business_unit or ""
        product_name = loan_product.product_name
        entity = loan_product.entity
        loan["business_unit"] = business_unit
        loan["product_name"] = product_name
        loan["entity"] = entity
        loan["sub_scheme"] = loan_product.sub_scheme
        loan["is_legacy"] = loan_product.is_legacy
        loan["policy_type_id"] = loan_product.policy_type_id
    if is_update:
        premium = round(float(loan.get("premium") or 0), 2)
        policy_details = {
            "binder_fees": calculate_binder_fees_amount(premium),
            "total_loan_schedule": loan.get("total_loan_schedule", ""),
            "total_policy_premium_collected": loan.get("total_policy_premium_collected"),
            "current_outstanding_balance": loan.get("current_outstanding_balance") or 0,
            "installment_amount": loan.get("instalment_amount") or 0,
        }
        old_policy.policy_details = policy_details
        old_policy.save()
        return
    policy, client = extract_policy_and_client_info(loan)
    serializer = ClientPolicyRequestSerializer(
        data={"client": client, "policy": policy},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()


def save_repayments(repayments):
    for repayment in repayments:
        product_id = repayment.get("product_id")
        if is_legacy_policy(product_id):
            policy_number = get_loan_id_from_legacy_loan(repayment.get("loan_external_id"))
        else:
            policy_number = repayment["loanId"]
        try:
            policy = Policy.objects.filter(policy_number=policy_number).first()
            if policy is None:
                create_policy(repayment)
            else:
                create_policy(loan=repayment, is_update=True, old_policy=policy)
            repayment_details = extract_repayment_details(repayment)

            serializer = PremiumPaymentSerializer(
                data=repayment_details
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            print(f"Error saving repayment {repayment}")
            print(e)


def is_legacy_policy(product_id) -> bool:
    legacy_ids = ["106", "107", "108"]
    return product_id in legacy_ids


def extract_repayment_details(repayment):
    product_id = repayment.get("product_id")
    if is_legacy_policy(product_id):
        policy_number = get_loan_id_from_legacy_loan(repayment.get("loan_external_id"))
    else:
        policy_number = repayment["loanId"]
    return {
        "policy_id": policy_number,
        "payment_date": repayment["transactionDate"],
        "amount": round(float(repayment.get("paidAmount", "0")), 2),
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
        print("Something went wrong fetching new loans, retrying")
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
    closed_loans = []
    try:
        response_status, data = query_closed_loans(tenant_id, start_date, end_date)
        print(f'response_status: {response_status}:: data: {data}')
        return data
    except Exception as e:
        print("Something went wrong fetching closed loans, retrying")
        print(e)
        return closed_loans


def create_claims_for_written_off_loans(written_off_loans):
    fin_claimant_details = ClaimantDetails.objects.filter(name="Fin").first()
    if fin_claimant_details is None:
        raise Exception("No Fin claimant details found")
    for loan in written_off_loans:
        product_id = loan.get("product_id")
        if is_legacy_policy(product_id):
            policy_number = get_loan_id_from_legacy_loan(loan.get("loan_external_id"))
        else:
            policy_number = loan["loanId"]
        try:
            policy = Policy.objects.filter(policy_number=policy_number).first()
            if policy is None:
                create_policy(loan)
                policy = Policy.objects.filter(policy_number=policy_number).first()
            else:
                create_policy(loan, is_update=True, old_policy=policy)
            claim = build_claim(loan, fin_claimant_details, policy)
            serializer = ClaimSerializer(
                data=claim
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            policy.policy_status = 'C'
            policy.closed_date = date.today()
            policy.save()

        except Exception as e:
            print(f"Error creating claim for {loan['loanId']}")
            print(e)


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


def build_claim(written_off_loan, fin_claimant_details, policy):
    loan_id = written_off_loan["loanId"]
    if policy:
        claim = {
            "policy_id": loan_id,
            "claim_type_id": 1,
            "claim_status": "Active",
            "claimant_name": fin_claimant_details.name,
            "claimant_surname": fin_claimant_details.surname,
            "claimant_id_number": fin_claimant_details.id_number,
            "claimant_id_type": 1,
            "claimant_email": fin_claimant_details.email,
            "claimant_phone": fin_claimant_details.phone_number,
            "claimant_bank_name": fin_claimant_details.bank,
            "claimant_bank_account_number": fin_claimant_details.account_number,
            "claimant_branch": fin_claimant_details.branch,
            "claimant_branch_code": fin_claimant_details.branch_code,
            "claim_assessed_by": "",
            "claim_amount": written_off_loan["written_off_amount"],
            "claim_details": {},
            "submitted_date": written_off_loan["written_off_date"],
        }
        return claim
