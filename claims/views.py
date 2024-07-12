import logging
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from drf_yasg import openapi
from claims.models import Claim
from drf_yasg.utils import swagger_auto_schema
from core.utils import CustomPagination
from .serializers import ClaimSerializer
from rest_framework import status
from datetime import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404

logger = logging.getLogger(__name__)


class ClaimCreateAPIView(APIView):
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="Create a new claim",
        request_body=ClaimSerializer,
        responses={
            201: openapi.Response("Created", ClaimSerializer),
            400: "Bad Request",
        },
    )
    def post(self, request):
        print(f'request: {request.data}')
        serializer = ClaimSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HTTPResponse.success(
                message="Resource created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        print(f'errors on creating claim: {serializer.errors}')
        return HTTPResponse.error(message=serializer.errors)

    @swagger_auto_schema(
        operation_description="Get all claims",
        responses={200: ClaimSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "claim_type",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Claim type ID",
                required=False,
            ),
            openapi.Parameter(
                "query",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search query",
                required=False,
            ),
            openapi.Parameter(
                "from",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Start date",
                required=False,
            ),
            openapi.Parameter(
                "to",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="End date",
                required=False,
            ),
        ],
    )
    def get(self, request):
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        claim_type = request.GET.get("claim_type", None)
        query = request.GET.get("query", None)
        claims = Claim.objects.all()
        print(f'request {request}')
        if query:
            claims = claims.filter(
                Q(claimant_name__icontains=query)
                | Q(claimant_surname__icontains=query)
                | Q(claimant_id_number__icontains=query)
                | Q(claimant_email__icontains=query)
                | Q(claimant_phone__icontains=query)
                | Q(policy__insurer__name__icontains=query)
                | Q(policy__policy_number__icontains=query)
            )

        if claim_type is not None:
            claims = claims.filter(claim_type_id=claim_type)
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            claims = claims.filter(created__gte=from_date)

        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            claims = claims.filter(created__lte=to_date)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(claims, request)
        serializer = ClaimSerializer(result_page, many=True)
        print(f'results {serializer.data}')
        claims_list = []
        for claim in serializer.data:
            claims_list.append({
                "id": claim["id"],
                "name": claim["name"],
                "policy": claim["policy"]["id"],
                "claim_type": claim["claim_type"]["id"],
                "claim_document": claim["claim_document"],
                "claim_status": claim['claim_status'],
                "claim_assessed_by": claim['claim_assessed_by'],
                "claim_assessment_date": claim['claim_assessment_date'],
                "claim_amount": claim['claim_amount'],
                "claims_details": "",
                "submitted_date": claim['submitted_date'],
                "claim_paid_date": claim['claim_paid_date'],
                "claimant_name": claim['claimant_name'],
                "claimant_surname": claim['claimant_surname'],
                "claimant_id_number": claim['claimant_id_number'],
                "claimant_email": claim['claimant_email'],
                "claimant_phone": claim['claimant_phone'],
                "claimant_bank_name": claim['claimant_bank_name'],
                "claimant_bank_account_number": claim['claimant_bank_account_number'],
                "claimant_branch": claim['claimant_branch'],
                "claimant_branch_code": claim['claimant_branch_code'],
                "claimant_id_type": claim['claimant_id_type'],
                "claim_rejected": claim['claim_rejected'],
                "rejected_date": claim['rejected_date'],
                "rejected_reason": claim['rejected_reason']
            })
        return HTTPResponse.success(
            message="Resource retrieved successfully",
            status_code=status.HTTP_200_OK,
            data={
                "results": claims_list,
                "count": paginator.page.paginator.count if paginator.page else 0,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        )


class ClaimDetailAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Retrieve a specific Claim by ID",
        responses={
            200: openapi.Response("Success", ClaimSerializer),
            404: "Claim not found",
        },
    )
    def get(self, request, pk):
        try:
            policy = get_object_or_404(Claim, pk=pk)
            serializer = ClaimSerializer(policy)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=serializer.data,
            )
        except Http404:
            return HTTPResponse.error(
                message="Claim not found", status_code=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        request_body=ClaimSerializer,
        responses={200: ClaimSerializer, 404: "Claim not found"},
        operation_description="Update a claim instance.",
    )
    def put(self, request, pk, format=None):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return HTTPResponse.error(
                message="Claim not found", status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ClaimSerializer(claim, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HTTPResponse.success(
                data=serializer.data, status_code=status.HTTP_200_OK
            )
        return HTTPResponse.error(
            message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        request_body=ClaimSerializer,
        responses={200: ClaimSerializer, 404: "Claim not found"},
        operation_description="Update a claim instance.",
    )
    def patch(self, request, pk, format=None):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return HTTPResponse.error(
                message="Claim not found", status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ClaimSerializer(claim, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return HTTPResponse.success(
                data=serializer.data, status_code=status.HTTP_200_OK
            )
        return HTTPResponse.error(
            message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )
