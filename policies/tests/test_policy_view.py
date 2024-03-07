from django.urls import reverse
from rest_framework import status
from clients.models import ClientDetails
from config.models import IdDocumentType, InsuranceCompany
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from policies.models import Policy
from policies.serializers import PolicySerializer

class PolicyViewTestCase(TenantTestCase):
    def setUp(self):
        self.c = TenantClient(self.tenant)
        self.id_document_type_data = {
            'type_name': 'Passport'
        }
        self.id_document_type = IdDocumentType.objects.create(**self.id_document_type_data)
        self.insurer_data = {
            'name': 'Insurer 1',
        }
        self.insurer = InsuranceCompany.objects.create(**self.insurer_data)

        

        self.client_data = {
            "first_name": "John",
            "last_name": "Doe",
            "primary_id_number": "123456789",
            "primary_id_document_type": self.id_document_type,  # Replace with actual ID document type ID
            "entity_type": "Individual",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "email": "john@example.com",
            "phone_number": "1234567890",
            "address_street": "123 Main St",
            "address_suburb": "Suburb",
            "address_town": "Town",
            "address_province": "Province",
        }
        self.client = ClientDetails.objects.create(**self.client_data)

        # Create some initial policies for testing
        self.policy_data = {
            "client": self.client,  # Replace with actual client ID
            "commencement_date": "2024-03-05",
            "expiry_date": "2025-03-05",
            "premium": "500.00",
            "policy_terms": 12,
            "policy_number": "POL-001",
            "insurer": self.insurer,  # Replace with actual insurer ID
            "policy_status": "QUOTATION"
        }
        self.invalid_policy_data = {
            # Invalid data for testing validation errors
        }
        self.policy = Policy.objects.create(**self.policy_data)
        self.policy_url = reverse('policy:create-policy')  # Assuming 'create-policy' is the endpoint name

    def test_create_policy(self):
        response = self.c.post(self.policy_url, self.policy_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Policy.objects.count(), 2)  # Check if a new policy was created

    def test_invalid_policy_data(self):
        response = self.c.post(self.policy_url, self.invalid_policy_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_policies(self):
        response = self.c.get(self.policy_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Policy.objects.count())

    def test_get_single_policy(self):
        policy_detail_url = reverse('policy:create-policy', kwargs={'pk': self.policy.pk})
        response = self.c.get(policy_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PolicySerializer(instance=self.policy)
        self.assertEqual(response.data, serializer.data)


    """
    # COMMENT OUT FOR NOW
    def test_update_policy(self):
        update_data = {
            "commencement_date": "2025-03-05",
            "expiry_date": "2026-03-05",
        }
        policy_detail_url = reverse('policy:create-policy', kwargs={'pk': self.policy.pk})
        response = self.c.patch(policy_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.policy.refresh_from_db()
        self.assertEqual(str(self.policy.commencement_date), update_data["commencement_date"])
        self.assertEqual(str(self.policy.expiry_date), update_data["expiry_date"])

    def test_delete_policy(self):
        policy_detail_url = reverse('policy:create-policy', kwargs={'pk': self.policy.pk})
        response = self.c.delete(policy_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Policy.objects.count(), 0)  # Check if the policy was deleted
    """
