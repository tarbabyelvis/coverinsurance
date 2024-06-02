from django.urls import path
from config.views import AgentList, BusinessSectorList, ClaimFieldsAPIView, ClaimTypeList, DocumentTypeList, \
    IdDocumentTypeList, InsuranceCompanyList, PolicyNameList, PolicyTypeFieldsAPIView, RelationshipsList

app_name = 'config'
urlpatterns = [
    path("policy-types", PolicyNameList.as_view(), name="policy-name-list"),
    path("insurance-company", InsuranceCompanyList.as_view(), name="insurance-company-list"),
    path("claim-types", ClaimTypeList.as_view(), name="claim-type-list"),
    path("document-types", DocumentTypeList.as_view(), name="document-type-list"),
    path("relationships", RelationshipsList.as_view(), name="relationships-list"),
    path("id-document-types", IdDocumentTypeList.as_view(), name="id-document-type-list"),
    path("business-sectors", BusinessSectorList.as_view(), name="business-sectors-list"),
    path("agents", AgentList.as_view(), name="agent-list"),
    path('policy-type-fields/', PolicyTypeFieldsAPIView.as_view(), name='policy-type-fields'),
    path('claim-type-fields/', ClaimFieldsAPIView.as_view(), name='claim-type-fields'),
]
