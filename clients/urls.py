from django.urls import path
from clients.views import *
from .views import *

app_name = 'clients'
urlpatterns = [
    path("", ClientsView.as_view(), name="create-get"),
    path('<int:pk>', ClientDetailView.as_view(), name='client-detail'),
    path("upload", UploadClients.as_view(), name="upload-clients"),
]
