from django.urls import path
from .views import *

app_name = "policy"

urlpatterns = [
    path("", PolicyView.as_view(), name="create-policy"),
    path("<int:pk>", PolicyDetailView.as_view(), name="policy-detail"),
    path(
        "client-and-policy",
        CreateClientAndPolicyAPIView.as_view(),
        name="client-and-policy",
    ),
    path(
        "client-and-policy",
        CreateClientAndPolicyAPIView.as_view(),
        name="client-and-policy",
    ),
    path(
        "upload-client-and-policy",
        UploadClientAndPolicyExcelAPIView.as_view(),
        name="client-and-policy-excel",
    ),
    path(
        "dependents/<int:policy_id>",
        PolicyDependenciesView.as_view(),
        name="policy-dependents",
    ),
    path(
        "beneficiaries/<int:policy_id>",
        PolicyBeneficiariesView.as_view(),
        name="policy-beneficiaries",
    ),
]
