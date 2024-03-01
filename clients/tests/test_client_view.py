import logging
from django.urls import reverse
from rest_framework import status
from ..models import IdDocumentType, ClientDetails
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

logger = logging.getLogger(__name__)

class ClientDetailsAPITests(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)

        self.id_document_type_data = {
            'type_name': 'Passport',
            # Include other required fields for IdDocumentType
        }
        self.id_document_type = IdDocumentType.objects.create(**self.id_document_type_data)


    def test_create_client(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'primary_id_number': '123456789',
            'primary_id_document_type': self.id_document_type.id,
            'entity_type': "INDIVIDUAL",
            'gender': "MALE",
        }
        url = reverse('clients:create-get')
        response = self.c.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        client_obj = ClientDetails.objects.filter().first()
        self.assertIsNotNone(client_obj)

    def test_get_clients(self):
        ClientDetails.objects.create(
            first_name='Jane',
            last_name='Doe',
            primary_id_number='987654321',
            primary_id_document_type=self.id_document_type,
        )

        url = reverse('clients:create-get')
        response = self.c.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data), 1)


