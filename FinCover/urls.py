from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("policies/", include("policies.urls")),
    path("claims/", include("claims.urls")),
    path("reports/", include("reports.urls")),
    path("clients/", include("clients.urls")),
    path("tenants/", include("tenants.urls")),
    path("jobs/", include("jobs.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
