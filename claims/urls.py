from django.urls import path
from .views import ClaimCreateAPIView

app_name = 'claim'

urlpatterns = [
    path('', ClaimCreateAPIView.as_view(), name='claim-create'),

]
