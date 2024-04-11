from django.urls import path
from .views import *

app_name = "jobs"

urlpatterns = [
    path(
        "credit-life-submission/<str:identifier>",
        LifeCreditAPIView.as_view(),
        name="credit-life-submission",
    ),
]
