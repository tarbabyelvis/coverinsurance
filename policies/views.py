import logging
from policies.models import Policy
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from rest_framework import status

from policies.services import upload_clients_and_policies
from .serializers import (
    ClientPolicyRequestSerializer,
    ClientPolicyResponseSerializer,
    PolicyDetailSerializer,
    PolicySerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)


class PolicyView(APIView):
    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_description="Create a new policy",
        request_body=PolicySerializer,
        responses={
            201: openapi.Response("Created", PolicySerializer),
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = PolicySerializer(data=request.data)
        if serializer.is_valid():
            try:
                logger.info("Validated data: %s", serializer.validated_data)
                # Save the validated data to create a new Policy instance
                serializer.save()
                return HTTPResponse.success(
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
        responses={200: "Success", 400: "Bad Request"},
    )
    def get(self, request):
        policies = Policy.all_objects.all()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(policies, request)
        serializer = PolicySerializer(result_page, many=True)

        return HTTPResponse.success(
            message="Request Successful",
            status_code=status.HTTP_200_OK,
            data={
                "results": serializer.data,
                "count": paginator.page.paginator.count if paginator.page else 0,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        )


class PolicyDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a specific policy by ID",
        responses={200: openapi.Response("Success", PolicyDetailSerializer)},
    )
    def get(self, request, pk):
        try:
            policy = get_object_or_404(Policy, pk=pk)
            serializer = PolicyDetailSerializer(policy)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=serializer.data,
            )
        except Http404:
            return HTTPResponse.error(
                message="Policy not found", status_code=status.HTTP_404_NOT_FOUND
            )


class CreateClientAndPolicyAPIView(APIView):

    @swagger_auto_schema(
        request_body=ClientPolicyRequestSerializer,
        responses={201: ClientPolicyResponseSerializer},
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = ClientPolicyRequestSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.save()
            return HTTPResponse.success(
                data=validated_data, status_code=status.HTTP_201_CREATED
            )
        else:
            return HTTPResponse.error(message=serializer.errors)


class UploadClientAndPolicyExcelAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=ClientPolicyRequestSerializer,
        responses={201: openapi.Response("Success")},
    )
    def post(self, request, *args, **kwargs):

        try:
            file_obj = request.data.get("file")
            upload_clients_and_policies(file_obj, [], [])

        except Exception as e:
            logger.error(e)
            return HTTPResponse.error(message=str(e))
