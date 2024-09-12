from django.urls import path
from .views import ClaimCreateAPIView, ClaimDetailAPIView, ProcessClaimAPIView, ApproveClaimAPIView, ReceiptClaimAPIView

app_name = "claim"

urlpatterns = [
    path("", ClaimCreateAPIView.as_view(), name="claim-create"),
    path("<int:pk>", ClaimDetailAPIView.as_view(), name="claim-detail"),
    path("<int:pk>", ClaimDetailAPIView.as_view(), name="claim-detail"),
    path("process_claim/<int:pk>/", ProcessClaimAPIView.as_view(), name="process claim"),
    path("approve_claim/<int:pk>/", ApproveClaimAPIView.as_view(), name="approve claim"),
    path("receipt_claim/<int:pk>/", ReceiptClaimAPIView.as_view(), name="receipt claim")
]
