import traceback
from datetime import datetime, date, timedelta
from typing import Final

from django.db.models import Q

from claims.models import Claim
from claims.serializers import ClaimSerializer
from config.enums import PolicyType
from config.models import ClaimantDetails, LoanProduct
from core.utils import first_day_of_previous_month, last_day_of_previous_month, get_loan_id_from_legacy_loan, \
    first_day_of_month_for_yesterday
from integrations.back_office import make_backoffice_request
from integrations.enums import Integrations
from integrations.guardrisk.guardrisk import GuardRisk
from integrations.models import IntegrationConfigs
from integrations.superbase import query_new_loans, query_repayments, query_closed_loans, query_written_off_loans, \
    query_premium_adjustments, query_loans_past_due
from integrations.utils import calculate_binder_fees_amount, calculate_commission_amount, \
    calculate_guard_risk_admin_amount
from jobs.models import TaskLog
from policies.models import Policy, PremiumPayment
from policies.serializers import PolicyDetailSerializer, PremiumPaymentSerializer, \
    ClientPolicyRequestSerializer
from policies.services import extract_employment_fields
from sms.services import warn_of_policy_lapse
from .models import Task

first_day_of_month_for_yesterday: date = first_day_of_month_for_yesterday()
last_day_of_previous_month: date = last_day_of_previous_month().date()
today_start_date: date = datetime.today().date()
yesterday: date = datetime.today().date() - timedelta(days=1)


def daily_job_postings(start_date=first_day_of_month_for_yesterday, end_date=yesterday):
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
                      end_date=yesterday):
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
        _, status = process_credit_life([], indlu_configs, start_date, end_date, is_daily_submission)

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


def life_funeral_daily(funeral_policies, nifty_configs, start_date=today_start_date, end_date=yesterday):
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
            pass
        # process_life_funeral([], nifty_configs, start_date, end_date, is_daily_submission)
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


def claims_daily(claims_fetched, nifty_configs, indlu_configs, start_date=today_start_date, end_date=yesterday):
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
            process_claims([], indlu_configs, start_date, end_date, is_daily_submission)
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
                   end_date=yesterday):
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
        Q(policy_status__in=('P', 'C', 'X'), policy_type__policy_type=policy_type.name,
          # TODO add the lapsed policies once notifications are done
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
    print(f'fetching fineract data from {start_date} to {end_date} for org {fineract_org_id}')
    # new_loans_status, new_loans = __fetch_new_policies_from_fin_connect(start_date, end_date, fineract_org_id)
    # fetch_and_update_loan_scores(new_loans_status, new_loans)
    # closed_status, closed_loans = __fetch_closed_loans_from_fin_connect(start_date, end_date, fineract_org_id)
    repay_status, repayments = __fetch_loan_repayments_from_fin_connect(start_date, end_date, fineract_org_id)
    # # loans_past_due = __fetch_past_loans_due(fineract_org_id)
    # # loans = __fetch_premium_adjustments_from_fin_connect(fineract_org_id)
    # save_new_loans(new_loans_status, new_loans)
    # update_closed_loans(closed_status, closed_loans)
    save_repayments(repay_status, repayments)
    # process_adjustments(loans)
    # process_unpaid_and_lapsed_policies(loans_past_due)
    print(f'Done processing fineract data fetch for {start_date} to {end_date} and tenant {fineract_org_id}')


def fetch_and_update_loan_scores(status, new_loans):
    if status == 200:
        loan_ids = get_loan_ids(new_loans)
        payload = {
            "loan_ids": loan_ids
        }
        print('fetching credit scores and employment details')
        status, scores = make_backoffice_request(
            tenant_id='fin-za',
            uri='/reports/application-score-and-employment-report',
            payload=payload
        )
        if status == 200:
            update_policy_with_application_score(scores, new_loans)


def process_adjustments(loans: list):
    policies = []
    for loan in loans:
        try:
            product_id = loan['product_id']
            external_id = loan.get("external_id")

            if is_legacy_policy(product_id):
                policy_number = get_loan_id_from_legacy_loan(external_id)
            else:
                policy_number = loan['loanId']

            policy = Policy.objects.filter(policy_number=policy_number).first()

            if policy is not None:
                # Get policy details from the specific policy instance
                policy_details = policy.policy_details or {}

                # Convert and round values from loan data
                initiation_fee = round(float(loan.get("initiation_fee", 0)), 2)
                service_fee = round(float(loan.get("service_fee", 0)), 2)
                interest_rate = round(float(loan.get("interest_rate", 0)), 2)

                # Update the policy details dictionary
                policy_details['loan_status'] = loan['loan_status']
                policy_details['initiation_fee'] = initiation_fee
                policy_details['service_fee'] = service_fee
                policy_details['interest_rate'] = interest_rate

                # Assign the updated policy details back to the instance
                policy.policy_details = policy_details
                policies.append(policy)
        except Exception as e:
            print(f"Error processing loan {loan}")
            print(e)

    # Bulk update policies with new details
    if policies:
        Policy.objects.bulk_update(policies, fields=['policy_details'])


DAYS_TO_LAPSE_POLICY_FOR_NON_PREMIUM_PAYMENT: Final = 60
DAYS_TO_WARN_FOR_NON_PREMIUM_PAYMENT: Final = 30


def process_unpaid_and_lapsed_policies(lapsed):
    lapsing_policies = []
    warned_policies = []
    client_details = []
    for loan in lapsed:
        try:
            days_past_due = float(loan['days_past_due'])
            if DAYS_TO_WARN_FOR_NON_PREMIUM_PAYMENT <= days_past_due < DAYS_TO_LAPSE_POLICY_FOR_NON_PREMIUM_PAYMENT:
                policy_number, _ = get_policy_number_and_external_id(loan)
                policy = Policy.objects.filter(policy_number=policy_number).first()
                if policy is not None and not policy.is_warned_of_non_payment:
                    policy.is_warned_of_non_payment = True
                    warned_policies.append(policy)
                    phone_number = policy.client.phone_number
                    if phone_number is not None or '':
                        business_unit = policy.business_unit
                        client_details.append({"phone_number": phone_number, "entity": business_unit})
            elif days_past_due > DAYS_TO_LAPSE_POLICY_FOR_NON_PREMIUM_PAYMENT:
                policy_number, _ = get_policy_number_and_external_id(loan)
                policy = Policy.objects.filter(policy_number=policy_number).first()
                if policy is not None and policy.policy_status != 'L':
                    policy.policy_status = 'L'
                    policy.closed_date = date.today()
                    lapsing_policies.append(policy)
        except Exception as e:
            print(f"Error lapsing loan{loan}")
            print(e)
    # Policy.objects.bulk_update(lapsing_policies, fields=['policy_status', 'closed_date'])
    # Policy.objects.bulk_update(warned_policies, fields=['is_warned_of_non_payment'])
    try:
        warn_of_policy_lapse(client_details)
    except Exception as e:
        print("Error notifying clients on unpaid loans")
        print(e)


def update_closed_loans(status, closed_loans):
    data = {
        "status": status,
        "closed_loans": len(closed_loans)
    }
    db_policies = []
    for loan in closed_loans:
        policy_number, _ = get_policy_number_and_external_id(loan)
        try:
            policy = Policy.objects.filter(policy_number=policy_number).first()
            if policy is None:
                create_policy(loan)
                policy = Policy.objects.filter(policy_number=policy_number).first()
            policy.policy_status = map_closure_reason(loan["closed_reason"])
            policy.closed_date = loan["closed_date"]
            policy_details = policy.policy_details or {}
            outstanding_balance = float(loan["current_outstanding_balance"])
            total_policy_premium_collected = float(loan["total_policy_premium_collected"])
            policy_details["current_outstanding_balance"] = outstanding_balance
            policy_details["total_policy_premium_collected"] = total_policy_premium_collected
            policy.policy_details = policy_details
            db_policies.append(policy)
        except Exception as e:
            print(f"Error updating closed loan  {loan}")
            print(e)
    Policy.objects.bulk_update(db_policies, fields=['policy_status', 'closed_date', 'policy_details'])
    save_fineract_job('closed_loans', status, data)


def map_closure_reason(closed_reason: str) -> str:
    if closed_reason == 'Withdrawn by client':
        return "X"
    elif closed_reason == 'Closed' or closed_reason == 'Overpaid':
        return "P"


def save_new_loans(status, new_loans):
    data = {
        "status": status,
        "new_loans": len(new_loans)
    }
    for loan in new_loans:
        try:
            print(f'was the loan updated ..{loan}')
            create_policy(loan)
        except Exception as e:
            print(f"Error saving new loan {loan['loanId']}")
            print(e)
    save_fineract_job('new_loans', status, data)


def save_fineract_job(task_type, status, data):
    task = fetch_tasks(task_type)
    log = create_task_logs(task)
    try:
        log.data = data
        if str(status).startswith("2"):
            log.status = "completed"
            log.save()
        else:
            log.status = "failed"
            log.save()
    except Exception as e:
        print(e)
        log.status = "failed"
        log.save()


def update_policy_with_application_score(scores, loans):
    loan_dict = {int(loan['loanId']): loan for loan in loans}

    for score in scores:
        print(f'score {score}')
        loan_id = int(score['loan_id'])
        if loan_id in loan_dict:
            loan = loan_dict[loan_id]
            loan['policy_details'] = loan.get('policy_details', {})
            loan['policy_details']['score'] = int(score.get('Score', 0))
            loan['policy_details']['score_band'] = score.get('Score Band', '')
            loan['email'] = score.get('client_email', '')
            loan['employer_name'] = score.get('employer_name', '')
            loan['job_title'] = score.get('position', '')
            loan['employment_start_date'] = score.get('employment_start_date', '')
            loan['employer_phone_number'] = score.get('employer_phone_number', '')
            loan['payment_frequency'] = score.get('payment_frequency', '')
            loan['marital_status'] = (score.get('marital_status') or 'Unknown').capitalize()


def get_loan_ids(loans):
    loan_ids = []
    for l in loans:
        loan_ids.append(l.get("loanId", ""))
    return loan_ids


def saving_application_score(scores):
    policies = []
    for score in scores:
        policy = Policy.objects.filter(loan_id=score['loan_id']).first()
        if policy is not None:
            policy_details = policy.policy_details or {}
            policy_details['score'] = int(score['Score']) or 0
            policy_details['score_band'] = score['Score Band'] or ''
            policy.policy_details = policy_details
            policies.append(policy)
    Policy.objects.bulk_update(policies, ['policy_details'])


def extract_policy_and_client_info(loan):
    policy_number, external_reference = get_policy_number_and_external_id(loan)
    premium = round(float(loan.get("premium") or 0), 2)
    total_premium = round(float(loan.get("total_premium") or 0), 2)
    policy_provider_type = loan["policy_type"]
    expiry_date = loan["maturityDate"]
    policy_term = loan["tenure"]
    outstanding_balance = round(float(loan.get("total_policy_premium_collected", 0)), 2)
    collected = round(float(loan.get("total_policy_premium_collected", 0)), 2)
    installment = round(float(loan.get("instalment_amount", 0)))
    schedule = round(float(loan.get("total_loan_schedule", 0)), 2)
    initiation_fee = round(float(loan.get("initiation_fee", 0)), 2)
    service_fee = round(float(loan.get("service_fee", 0)), 2)
    interest_rate = round(float(loan.get("interest_rate", 0)), 2)
    existing_policy_details = loan.get("policy_details", {})
    new_policy_details = {
        "binder_fees": calculate_binder_fees_amount(premium),
        "total_loan_schedule": schedule,
        "total_policy_premium_collected": collected,
        "current_outstanding_balance": outstanding_balance,
        "installment_amount": installment,
        "loan_status": loan.get("loan_status"),
        "initiation_fee": initiation_fee,
        "service_fee": service_fee,
        "interest_rate": interest_rate
    }
    merged_policy_details = {**existing_policy_details, **new_policy_details}
    policy = {
        "policy_type": 1,
        "insurer": 1 if policy_provider_type == "Internal Credit Life" else 2,
        "policy_number": policy_number,
        "external_reference": external_reference,
        "sum_insured": round(float(loan.get("loan_amount") or 0), 2),
        "premium": premium,
        "total_premium": total_premium,
        "commencement_date": loan.get("disbursementDate") or date.today().strftime("%Y-%m-%d"),
        "policy_status": "A",
        "expiry_date": expiry_date or date.today().strftime("%Y-%m-%d"),
        "product_name": loan["productName"],
        "policy_term": policy_term,
        "admin_fee": calculate_guard_risk_admin_amount(premium),
        "commission_amount": calculate_commission_amount(premium),
        "commission_percentage": 7.50,
        "premium_frequency": "Monthly",
        "commission_frequency": "Monthly",
        "policy_provider_type": policy_provider_type,
        "business_unit": loan.get("business_unit", ""),
        "entity": loan.get("entity") or "",
        "is_legacy": loan.get("is_legacy"),
        "sub_scheme": loan.get("sub_scheme") or "",
        "policy_type_id": loan.get("policy_type_id", ""),
        "loan_id": loan.get("loanId", ""),
        "policy_details": merged_policy_details
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
        'marital_status': loan.get('marital_status', ''),
        "email": loan.get("email", ""),
        "phone_number": loan.get("mobile_number", ""),
        "entity_type": "Individual",
        'employer_name': loan.get('employer_name', ''),
        'job_title': loan.get('position', ''),
        'employment_date': loan.get('employment_start_date', ''),
        'employer_phone_number': loan.get('employer_phone_number', ''),
        'payment_frequency': loan.get('payment_frequency', ''),
    }
    client = extract_employment_fields(client)
    return policy, client


def create_policy(loan, is_update: bool = False, old_policy=None):
    product_id = int(loan.get("product_id"))
    loan_product = LoanProduct.objects.filter(product_id=product_id).first()
    if loan_product is not None:
        business_unit = loan_product.business_unit
        product_name = loan_product.product_name
        entity = loan_product.entity
        subscheme = loan_product.sub_scheme
        is_legacy = loan_product.is_legacy
        policy_type_id = loan_product.policy_type_id
        loan["business_unit"] = business_unit
        loan["product_name"] = product_name
        loan["entity"] = entity
        loan["sub_scheme"] = subscheme
        loan["is_legacy"] = is_legacy
        loan["policy_type_id"] = policy_type_id
    if is_update:
        premium = round(float(loan.get("premium") or 0), 2)
        total_policy_premium_collected = round(float(loan.get("total_policy_premium_collected") or 0), 2)
        current_outstanding_balance = round(float(loan.get("current_outstanding_balance") or 0), 2)
        schedule = round((float(loan.get("total_loan_schedule", "") or 0)), 2)
        policy_details = old_policy.policy_details or {}
        policy_details["binder_fees"]: calculate_binder_fees_amount(premium)
        policy_details["total_loan_schedule"]: schedule
        policy_details["total_policy_premium_collected"]: total_policy_premium_collected
        policy_details["current_outstanding_balance"]: current_outstanding_balance
        policy_details["installment_amount"]: loan.get("instalment_amount") or 0

        old_policy.policy_details = policy_details
        old_policy.save()
        return
    policy, client = extract_policy_and_client_info(loan)
    serializer = ClientPolicyRequestSerializer(
        data={"client": client, "policy": policy},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()


def save_repayments(status, repayments):
    data = {
        "status": status,
        "repayments": len(repayments),
    }
    for repayment in repayments:
        policy_number, _ = get_policy_number_and_external_id(repayment)
        try:
            policy_id = None
            policy = Policy.objects.filter(policy_number=policy_number).first()
            if policy is not None:
                if policy.policy_status not in ['L', 'X']:
                    policy_id = policy.id
                    policy_details = policy.policy_details

                    collected = round(float(repayment.get("total_policy_premium_collected")), 2)
                    outstanding = round(float(repayment.get("current_outstanding_balance") or 0), 2)

                    policy_details["total_policy_premium_collected"] = collected
                    policy_details["current_outstanding_balance"] = outstanding

                    policy.policy_details = policy_details
                    policy.save()
            else:
                create_policy(repayment)
                policy_created = Policy.objects.filter(policy_number=policy_number).first()

                if policy_created:
                    policy_id = policy_created.id
                    policy = policy_created
                else:
                    print(f"Policy creation failed for repayment {repayment}")
                    continue

            if policy and policy.policy_status not in ['L', 'X']:
                repayment_details = extract_repayment_details(repayment, policy_id)
                serializer = PremiumPaymentSerializer(data=repayment_details)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        except Exception as e:
            print(f"Error saving repayment {repayment}")
            print(e)
    save_fineract_job('repayments', status, data)


def is_legacy_policy(product_id) -> bool:
    legacy_ids = ["106", "107", "108", 106, 107, 108]
    return product_id in legacy_ids


def get_policy_number_and_external_id(loan):
    product_id = loan.get("product_id")
    external_id = loan.get("loan_external_id")
    if is_legacy_policy(product_id):
        policy_number = get_loan_id_from_legacy_loan(external_id)
        return policy_number, external_id
    return loan["loanId"], external_id


def extract_repayment_details(repayment, policy_id):
    policy_number, _ = get_policy_number_and_external_id(repayment)
    return {
        "policy_id": policy_id,
        "policy_number": policy_number,
        "payment_date": repayment["transactionDate"],
        "amount": round(float(repayment.get("paidAmount", "0")), 2),
        "transaction_type": repayment["paymentType"] or "",
        "payment_method": repayment["paymentType"] or "",
        "transaction_id": repayment["transaction_id"],
    }


def __fetch_new_policies_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching new loans")
    new_loans = []
    try:
        response_status, _, data = query_new_loans(tenant_id, start_date, end_date)
        print(f'new policies status: {response_status}:: data: {data}')
        return 200, data
    except Exception as e:
        print("Something went wrong fetching new loans, retrying")
        print(e)
        return 0, new_loans


def __fetch_loan_repayments_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching loan repayments")
    collections = []
    try:
        response_status, _, data = query_repayments(tenant_id, start_date, end_date)
        print(f'repayments status: {response_status}:: data: {data}')
        return 200, data
    except Exception as e:
        print("Something went wrong fetching loan repayments")
        print(e)
        return 0, collections


def __fetch_closed_loans_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching closed loans")
    closed_loans = []
    try:
        response_status, _, data = query_closed_loans(tenant_id, start_date, end_date)
        print(f'closed loans status: {response_status}:: data: {data}')
        return 200, data
    except Exception as e:
        print("Something went wrong fetching closed loans, retrying")
        print(e)
        return 0, closed_loans


def __fetch_premium_adjustments_from_fin_connect(tenant_id):
    print("Fetching premium loans")
    loans = []
    try:
        response_status, _, data = query_premium_adjustments(tenant_id)
        print(f'response_status: {response_status}')
        return data
    except Exception as e:
        print("Something went wrong fetching adjustments loans, retrying")
        print(e)
        return loans


def create_claims_for_written_off_loans(written_off_loans):
    fin_claimant_details = ClaimantDetails.objects.filter(name="Fin").first()
    if fin_claimant_details is None:
        raise Exception("No Fin claimant details found")
    for loan in written_off_loans:
        policy_number, _ = get_policy_number_and_external_id(loan)
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


def __fetch_written_off_loans_from_fin_connect(start_date: date, end_date: date, tenant_id):
    print("Fetching written off loans")
    written_off_loans = []
    try:
        response_status, _, data = query_written_off_loans(tenant_id, start_date, end_date)
        print(f'response_status: {response_status}:: data: {data}')
        return data
    except Exception as e:
        print("Something went wrong fetching written loans")
        print(e)
        return written_off_loans


def __fetch_past_loans_due(tenant_id):
    print("Fetching loans past due")
    loans_past = []
    try:
        response_status, _, data = query_loans_past_due(tenant_id)
        print(f'response_status: {response_status}')
        return data
    except Exception as e:
        print("Something went wrong fetching loan past due")
        print(e)
        return loans_past


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
