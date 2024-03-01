
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from clients.services import upload_clients
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from rest_framework import status
from clients.models import ClientDetails
from .serializers import ClientDetailsSerializer

logger = logging.getLogger(__name__)

class ClientsView(APIView):
    def post(self, request):
        serializer = ClientDetailsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                logger.info("Validated data: %s", serializer.validated_data)
                # Save the validated data to create a new ClientDetails instance
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
    def get(self, request):
        clients = ClientDetails.objects.all()
        serializer = ClientDetailsSerializer(clients, many=True)
        return  HTTPResponse.success(
            message="Request Successful",
            status_code=status.HTTP_200_OK,
            data = serializer.data
        )

class UploadClients(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            file_obj = request.data["file"]
            logger.info("File object: %s", file_obj)
            upload_clients(file_obj)
            return  HTTPResponse.success(
                message="Resource created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return HTTPResponse.error(message=str(e))
