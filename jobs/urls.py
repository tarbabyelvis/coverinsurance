from django.urls import path
from .views import *

app_name = "jobs"

urlpatterns = [
    path(
        "daily-job-submission/",
        DailyJobPostingAPIView.as_view(),
        name="daily-job-submission",
    ),
    path(
        "monthly-job-submission/",
        MonthlyJobPostingsAPIView.as_view(),
        name="monthly-job-submission",
    ),
    path(
        "finconnect-data_fetch-job/",
        FetchFinConnectDataAPIView.as_view(),
        name="finconnect-data_fetch-job",
    )

]
