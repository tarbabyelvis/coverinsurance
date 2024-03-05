
from email.policy import Policy
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from claims.models import Claim
from claims.serializer import ClaimSerializer
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class ClaimView(APIView):
    @swagger_auto_schema(
        operation_description="Create a new claim",
        request_body=ClaimSerializer,
        responses={
            201: openapi.Response("Created", ClaimSerializer),
            400: "Bad Request",
        }
    )

    def post(self, request):
        serializer = ClaimSerializer(data=request.data)
        if serializer.is_valid():
            try:
                logger.info("Validated data: %s", serializer.validated_data)
                # Save the validated data to create a new Policy instance
                serializer.save()
                return  HTTPResponse.success(
                    message="Resource created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return HTTPResponse.error(message=str(e))
        else:
            return HTTPResponse.error(message=serializer.errors)
        
    # get all clients
    @swagger_auto_schema(
        operation_description="Endpoint Operation Description for GET",
        responses={
            200: "Success",
            400: "Bad Request"
        }
    )
    def get(self, request):
        claims = Claim.objects.all()
        serializer = ClaimSerializer(claims, many=True)
        return  HTTPResponse.success(
            message="Request Successful",
            status_code=status.HTTP_200_OK,
            data = serializer.data
        )
