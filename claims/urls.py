from django.urls import path
from .views import *

urlpatterns = [
    path('', ClaimCreateAPIView.as_view(), name='claim-create'),

]
