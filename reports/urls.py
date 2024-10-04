from django.urls import path

from claims.models import Claim
from .views import *

urlpatterns = [
    path("bordrex-report", BordrexReportView.as_view(), name="bordrex-report"),
    path(
        "bordrex-report-excel",
        BordrexExcelExportView.as_view(),
        name="bordrex-report-excel",
    ),
    path(
        "bordrex-quarterly-report",
        BordrauxQuarterlyReportView.as_view(),
        name="bordrex-quarterly-report",
    ),
    path(
        "bordrex-quarterly-report-excel",
        BordrauxQuarterlyExportReportView.as_view(),
        name="bordrex-quarterly-report-excel",
    ),
    path(
        "policies-summary-report",
        PoliciesSummaryReportView.as_view(),
        name="policies-report",
    ),
    path(
        "policies-summary-report-download",
        PoliciesSummaryReportExcelView.as_view(),
        name="policies-report-excel",
    ),
    path(
        "claims-summary-report",
        ClaimsSummaryReportView.as_view(),
        name="claims-report",
    ),
    path(
        "claims-summary-report-download",
        ClaimsSummaryReportExcelView.as_view(),
        name="claims-report-excel",
    ),
    path(
        "clients-summary-report",
        ClientsSummaryReportView.as_view(),
        name="clients-report",
    ),
    path(
        "clients-summary-report-download",
        ClientsSummaryReportExcelView.as_view(),
        name="clients-report-excel",
    ),
]
