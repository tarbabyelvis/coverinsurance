from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView

from users.serializers import CustomTokenObtainPairView

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Insurance Cover",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="it@fin.africa"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("admin/", admin.site.urls, name="admin-app"),
    path("v1/policies/", include("policies.urls"), name="policies-app"),
    path("v1/claims/", include("claims.urls"), name="claims-app"),
    path("v1/reports/", include("reports.urls"), name="reports-app"),
    path("v1/clients/", include("clients.urls"), name="clients-app"),
    path("v1/tenants/", include("tenants.urls"), name="tenants-app"),
    path("v1/config/", include("config.urls"), name="config-app"),
    path("v1/jobs/", include("jobs.urls"), name="jobs-app"),
    path("v1/auth/", include("users.urls"), name="authentication-app"),
    path('v1/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
