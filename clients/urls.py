from django.urls import path
from clients.views import ClientsView
from .views import *

app_name = 'clients'
urlpatterns = [
    path("", ClientsView.as_view(), name="create-get"),
    path("upload", UploadClients.as_view(), name="upload-clients"),
]
