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

        serializer = ClaimSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HTTPResponse.success(
                message="Resource created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
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
                required=True,
            ),
            openapi.Parameter(
                "to",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="End date",
                required=True,
            ),
        ],
    )
    def get(self, request):
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        claim_type = request.GET.get("claim_type", None)
        query = request.GET.get("query", None)
        claims = Claim.objects.all()

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
        return HTTPResponse.success(
            message="Resource retrieved successfully",
            status_code=status.HTTP_200_OK,
            data={
                "results": serializer.data,
                "count": paginator.page.paginator.count if paginator.page else 0,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        )
