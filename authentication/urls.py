from django.urls import path
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CustomTokenObtainPairView

urlpatterns = [
    # Rest Framework Basic Token
    path('api-token-auth/', views.obtain_auth_token),
    # JWT Based Tokens
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenObtainPairView.as_view(), name='token_refresh'),
]