from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls, name="admin-app"),
    path("v1/policies/", include("policies.urls"), name="policies-app"),
    path("v1/claims/", include("claims.urls"), name="claims-app"),
    path("v1/reports/", include("reports.urls"), name="reports-app"),
    path("v1/clients/", include("clients.urls"), name="clients-app"),
    path("v1/tenants/", include("tenants.urls"), name="tenants-app"),
    path("v1/jobs/", include("jobs.urls"), name="jobs-app"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
