
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
        # Create a sample Excel file for testing
        # excel_file_content = b"First Name,Middlename,Last Name,ID Number,ID Type,Entity Type,Gender,Marital Status,Date of Birth,Email,Phone number,Address Street,Address Suburb,Address Town,Address Province\nJohn,Doe,Smith,1234567,Passport,Individual,Male,Single,1990-01-01,john@example.com,1234567890,Street,Suburb,Town,Province\n"
        # excel_file = InMemoryUploadedFile(
        #     'test.xlsx', excel_file_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        #     len(excel_file_content.getvalue()), None
        # )

        # CSV data
        
        # Create InMemoryUploadedFile
        excel_file = mock_upload_excel()
        # Make a POST request to the API endpoint
        url = reverse("clients:upload-clients")
        response = self.c.post(url, {"file": excel_file}, format="multipart")
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