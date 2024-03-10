
from rest_framework.views import APIView
from core.http_response import HTTPResponse
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema

class PolicyNameList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of policy names",
        responses={200: PolicyNameSerializer(many=True)}
    )
    def get(self, request):
        policy_names = PolicyName.objects.all()
        serializer = PolicyNameSerializer(policy_names, many=True)
        return HTTPResponse.success(data=serializer.data)

class InsuranceCompanyList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of insurance companies",
        responses={200: InsuranceCompanySerializer(many=True)}
    )
    def get(self, request):
        insurance_companies = InsuranceCompany.objects.all()
        serializer = InsuranceCompanySerializer(insurance_companies, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class ClaimTypeList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of claim types",
        responses={200: ClaimTypeSerializer(many=True)}
    )
    def get(self, request):
        claim_types = ClaimType.objects.all()
        serializer = ClaimTypeSerializer(claim_types, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class DocumentTypeList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of document types",
        responses={200: DocumentTypeSerializer(many=True)}
    )
    def get(self, request):
        document_types = DocumentType.objects.all()
        serializer = DocumentTypeSerializer(document_types, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class RelationshipsList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list relationships",
        responses={200: DocumentTypeSerializer(many=True)}
    )
    def get(self, request):
        relationships = DocumentType.objects.all()
        serializer = DocumentTypeSerializer(relationships, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class IdDocumentTypeList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list ID Document types",
        responses={200: DocumentTypeSerializer(many=True)}
    )
    def get(self, request):
        id_document_types = IdDocumentType.objects.all()
        serializer = IdDocumentTypeSerializer(id_document_types, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class BusinessSectorList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of Business Sectors",
        responses={200: BusinessSectorSerializer(many=True)}
    )
    def get(self, request):
        business_sectors = BusinessSector.objects.all()
        serializer = BusinessSectorSerializer(business_sectors, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class AgentList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list ID Document types",
        responses={200: AgentSerializer(many=True)}
    )
    def get(self, request):
        business_sectors = Agent.objects.all()
        serializer = AgentSerializer(business_sectors, many=True)
        return HTTPResponse.success(data=serializer.data)
    
class PolicyTypeFieldsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list ID Document types",
        responses={200: AgentSerializer(many=True)}
    )
    def get(self, request, format=None):
        policy_type = request.query_params.get('policy_type')

        if not policy_type:
            return HTTPResponse.error(message="Please provide a policy type")

        policy_type_fields = PolicyTypeFields.objects.filter(id=policy_type)
        serializer = PolicyTypeFieldsSerializer(policy_type_fields, many=True)
        return HTTPResponse.success(serializer.data)
    

class ClaimFieldsAPIView(APIView):
    def get(self, request, format=None):
        claim_type = request.query_params.get('claim_type')

        if not claim_type:
            return HTTPResponse.error(message="Please provide a claim type")

        claim_type_fields = ClaimFields.objects.filter(id=claim_type)
        serializer = ClaimFieldsSerializer(claim_type_fields, many=True)
        return HTTPResponse.success(serializer.data)