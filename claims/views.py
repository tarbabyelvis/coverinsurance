import logging
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from claims.models import Claim
from drf_yasg.utils import swagger_auto_schema
from .serializers import ClaimSerializer
from rest_framework import status

logger = logging.getLogger(__name__)


class ClaimCreateAPIView(APIView):
    pagination_class = PageNumberPagination

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
    )
    def get(self, request):
        claims = Claim.objects.all()
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
