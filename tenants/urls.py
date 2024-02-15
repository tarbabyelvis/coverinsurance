from django.urls import path
from .views import *

app_name = "tenants"

urlpatterns = [path("get-tenants", GetTenants.as_view())]
