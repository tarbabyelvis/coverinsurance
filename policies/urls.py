from django.urls import path
from .views import *

urlpatterns = [
    path("", PolicyView.as_view(), name="create-policy"),
]
