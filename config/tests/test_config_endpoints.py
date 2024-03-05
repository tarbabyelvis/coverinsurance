from django.urls import reverse
from rest_framework import status
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from config.models import Agent, BusinessSector, ClaimType, DocumentType, IdDocumentType, InsuranceCompany, PolicyName, Relationships

class PolicyNameListTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        PolicyName.objects.create(name='Policy 1', policy_type='FUNERAL_COVER')
        PolicyName.objects.create(name='Policy 2', policy_type='CREDIT_LIFE')

    def test_policy_name_list(self):
        
        response = self.c.get(reverse('config:policy-name-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)

class InsuranceCompanyListTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        InsuranceCompany.objects.create(name='Company 1')
        InsuranceCompany.objects.create(name='Company 2')

    def test_insurance_company_list(self):
        
        response = self.c.get(reverse('config:insurance-company-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)

class ClaimTypeTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        ClaimType.objects.create(name='Accident')
        ClaimType.objects.create(name='Death')

    def test_claim_type_list(self):
        
        response = self.c.get(reverse('config:claim-type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)


class DocumentTypeTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        DocumentType.objects.create(document_type='Passport')
        DocumentType.objects.create(document_type='Logbook')

    def test_document_type_list(self):
        
        response = self.c.get(reverse('config:document-type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)


class RelationshipsTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        Relationships.objects.create(name='Father')
        Relationships.objects.create(name='Sister')

    def test_relationships_list(self):
        response = self.c.get(reverse('config:relationships-list'))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)

class IdDocumentTypeTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        IdDocumentType.objects.create(type_name='National ID')
        IdDocumentType.objects.create(type_name='Passport')

    def test_id_document_type_list(self):
        response = self.c.get(reverse('config:id-document-type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)


class BusinessSectorTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        BusinessSector.objects.create(sector='Father')
        BusinessSector.objects.create(sector='Sister')

    def test_business_sector_list(self):
        response = self.c.get(reverse('config:business-sectors-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)


class AgentTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)
        Agent.objects.create(agent_name='John Doe', entity_type="INDIVIDUAL", phone_number="07993754", email="john@example.com")
        Agent.objects.create(agent_name='Fin Africa', entity_type="ORGANIZATION", phone_number="07975793754", email="fin@example.com")

    def test_agent_list(self):
        
        response = self.c.get(reverse('config:agent-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["data"]), 2)


