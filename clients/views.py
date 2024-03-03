
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from clients.services import upload_clients
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from rest_framework import status
from clients.models import ClientDetails
from .serializers import ClientDetailsSerializer, ExcelSchema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from marshmallow import ValidationError

logger = logging.getLogger(__name__)

class ClientsView(APIView):
    @swagger_auto_schema(
        operation_description="Create a new client",
        request_body=ClientDetailsSerializer,
        responses={
            201: openapi.Response("Created", ClientDetailsSerializer),
            400: "Bad Request",
        }
    )

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
    @swagger_auto_schema(
        operation_description="Endpoint Operation Description for GET",
        responses={
            200: "Success",
            400: "Bad Request"
        }
    )
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

    @swagger_auto_schema(
        operation_description="Upload client data from an Excel file",
        manual_parameters=[
            openapi.Parameter(
                name='file', in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Excel file containing client data'
            ),
            openapi.Parameter(
                name='columns', in_=openapi.IN_FORM,
                type=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "middle_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "id_number": openapi.Schema(type=openapi.TYPE_STRING),
                        "id_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "entity_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "gender": openapi.Schema(type=openapi.TYPE_STRING),
                        "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
                        "date_of_birth": openapi.Schema(type=openapi.TYPE_STRING),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                        "address_street": openapi.Schema(type=openapi.TYPE_STRING),
                        "address_suburb": openapi.Schema(type=openapi.TYPE_STRING),
                        "address_town": openapi.Schema(type=openapi.TYPE_STRING),
                        "address_province": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                    # required=["first_name", "last_name", "id_number"]
                ),
                required=True,
                description='Mapping of column names in the Excel file to field names in the database (JSON format)'
            )
        ],
        responses={
            201: "Resource created successfully",
            400: "Bad Request"
        }
    )
        

    def post(self, request):
        try:
            schema = ExcelSchema()
            schema.load(dict(request.data))

            file_obj = request.data.get("file")
            columns_map = request.data.get("columns")

            if file_obj is None or columns_map is None:
                return HTTPResponse.error(message="File or columns map is missing in the request.")

            upload_clients(file_obj, columns_map)
            return HTTPResponse.success(
                message="Resource created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            print("Validation Error: ", e)
            return HTTPResponse.error(message=e.messages)
        except KeyError as e:
            print("Key Error: ", e)
            return HTTPResponse.error(message="Missing key in request data: " + str(e))
        except Exception as e:
            print("Error: ", e)
            return HTTPResponse.error(message=str(e))
