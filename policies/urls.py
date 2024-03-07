from django.urls import path
from .views import *

app_name = 'policy'

urlpatterns = [
    path("", PolicyView.as_view(), name="create-policy"),
]
