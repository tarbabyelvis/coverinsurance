from django.urls import path
from .views import *

app_name = "jobs"

urlpatterns = [
    path(
        "credit-life-submission/<str:report_type>",
        LifeCreditAPIView.as_view(),
        name="credit-life-submission",
    ),
]
