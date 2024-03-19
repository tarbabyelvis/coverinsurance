from django.urls import path
from .views import *

urlpatterns = [
    path("bordrex-report", BordrexReportView.as_view(), name="bordrex-report"),
    path(
        "bordrex-report-excel",
        BordrexExcelExportView.as_view(),
        name="bordrex-report-excel",
    ),
]
