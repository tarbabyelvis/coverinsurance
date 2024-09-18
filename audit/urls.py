from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from audit.views import ClaimAuditAPIView

app_name = "audit"

urlpatterns = [
    path("claim_audit/<int:pk>/", ClaimAuditAPIView.as_view(), name="audit-detail"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
