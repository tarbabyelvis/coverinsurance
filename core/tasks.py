import datetime

from celery import shared_task
from django_q.tasks import schedule

from claims.orm_queries import fetch_claims_needing_review
from core.enums import ClaimStatus


@shared_task
def mark_claims_for_review():
    try:
        claims_to_review = fetch_claims_needing_review()
        for claim in claims_to_review:
            claim.claim_status = ClaimStatus.REVIEW
            claim.save()
    except Exception as e:
        print(e)


schedule(
    'core.tasks.mark_claims_for_review',
    schedule_type='D',  # D stands for daily
    next_run=datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(1, 0, 0))  # Schedule the first run for tomorrow at 1 AM
)
# run this when starting the app : python manage.py qcluster