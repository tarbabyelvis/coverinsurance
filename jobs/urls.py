from django.urls import path
from .views import *

app_name = "jobs"

urlpatterns = [
    path(
        "credit-life-submission/",
        LifeCreditAPIView.as_view(),
        name="credit-life-submission",
    ),
    path(
        "credit-life-daily-submission/",
        LifeCreditDailyAPIView.as_view(),
        name="credit-life-daily-submission",
    ),
    path(
        "funeral-daily-submission/",
        FuneralCoverDailyAPIView.as_view(),
        name="funeral-daily-submission",
    ),
    path(
        "funeral-submission/",
        FuneralCoverAPIView.as_view(),
        name="funeral-submission",
    ),
]
