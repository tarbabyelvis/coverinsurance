from django.urls import path
from .views import ClaimCreateAPIView, ClaimDetailAPIView, RetrenchmentClaimAPIView

app_name = "claim"

urlpatterns = [
    path("", ClaimCreateAPIView.as_view(), name="claim-create"),
    path("<int:pk>", ClaimDetailAPIView.as_view(), name="claim-detail"),
    path("<int:pk>", ClaimDetailAPIView.as_view(), name="claim-detail"),
    path("process_retrenchment/<int:pk>/", RetrenchmentClaimAPIView.as_view(), name="retrenchment claim")
]
