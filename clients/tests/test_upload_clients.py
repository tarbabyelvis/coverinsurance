
import json
import logging
from django.urls import reverse
from rest_framework import status
from clients.factory.clients_excel import mock_upload_excel
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from io import BytesIO
import pandas as pd

logger = logging.getLogger(__name__)
# Test file upload
class UploadClientsTest(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)


    def test_upload_clients_success(self):
        
        # Create InMemoryUploadedFile
        excel_file, columns = mock_upload_excel()
        # Make a POST request to the API endpoint
        url = reverse("clients:upload-clients")
        # response = self.c.post(url, {"file": excel_file, "columns": columns}, format="multipart")
        columns_data = json.dumps(columns)
        response = self.c.post(url, {"file": excel_file, "columns": columns_data}, format="multipart")
        logger.info(f"upload correct: {response.content}")

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Resource created successfully")

    def test_upload_clients_failure(self):
        # Make a POST request with missing file parameter
        url = reverse("clients:upload-clients")
        response = self.c.post(url, {}, format="multipart")
        logger.info(f"upload incorrect: {response.content}")
        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)