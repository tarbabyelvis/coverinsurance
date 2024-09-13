from django.urls import path

from django.conf import settings
from .views import ClaimCreateAPIView, ClaimDetailAPIView, ProcessClaimAPIView, ApproveClaimAPIView, \
    ReceiptClaimAPIView, AddDocuments, AddDocTemplates, GetClaimDocumentsView
from django.conf.urls.static import static
app_name = "claim"

urlpatterns = [
    path("", ClaimCreateAPIView.as_view(), name="claim-create"),
    path("<int:pk>", ClaimDetailAPIView.as_view(), name="claim-detail"),
    #path("<int:pk>", ClaimDetailAPIView.as_view(), name="claim-detail"),
    path("process_claim/<int:pk>/", ProcessClaimAPIView.as_view(), name="process claim"),
    path("approve_claim/<int:pk>/", ApproveClaimAPIView.as_view(), name="approve claim"),
    path("receipt_claim/<int:pk>/", ReceiptClaimAPIView.as_view(), name="receipt claim"),
    path("add_documents/", AddDocuments.as_view(), name="add-new-document"),
    path("add_templates/", AddDocTemplates.as_view(), name="add-new-template"),
    path("get_claim_files/<int:pk>", GetClaimDocumentsView.as_view(), name="get_claim_files"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)