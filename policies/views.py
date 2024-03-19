import logging
from policies.constants import (
    CLIENT_COLUMNS,
    CLIENT_COLUMNS_BORDREX,
    POLICY_COLUMNS,
    POLICY_COLUMNS_BORDREX,
)
from policies.models import Beneficiary, Dependant, Policy, PremiumPayment
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from rest_framework import status
from policies.services import upload_clients_and_policies
from .serializers import (
    BeneficiarySerializer,
    ClientPolicyRequestSerializer,
    ClientPolicyResponseSerializer,
    DependantSerializer,
    PolicyDetailSerializer,
    PolicyListSerializer,
    PolicySerializer,
    PremiumPaymentSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from datetime import datetime

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
        serializer = PolicySerializer(
            data=request.data,
            context={"request": request},
        )
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
            return HTTPResponse.error(
                message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
            )

    # get all clients
    @swagger_auto_schema(
        operation_description="Endpoint Operation Description for GET",
        responses={
            201: openapi.Response("Request Successful", PolicyListSerializer),
            400: "Bad Request",
        },
        manual_parameters=[
            openapi.Parameter(
                "policy_type",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Policy type ID",
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
        policy_type = request.GET.get("policy_type", None)
        query = request.GET.get("query", None)
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        policies = Policy.objects.all()
        if query:
            policies = policies.filter(
                Q(client__first_name__icontains=query)
                | Q(client__last_name__icontains=query)
                | Q(client__middle_name__icontains=query)
                | Q(client__external_id__icontains=query)
                | Q(client__email__icontains=query)
                | Q(client__phone_number__icontains=query)
                | Q(insurer__name__icontains=query)
                | Q(policy_number__icontains=query)
                | Q(external_reference__icontains=query)
            )
        if policy_type != None:
            policies = policies.filter(policy_type_id=policy_type)

        if policy_type is not None:
            policies = policies.filter(policy_type_id=policy_type)

        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            policies = policies.filter(start_date__gte=from_date)

        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policies = policies.filter(end_date__lte=to_date)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(policies, request)
        serializer = PolicyListSerializer(result_page, many=True)

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
        responses={
            200: openapi.Response("Success", PolicyDetailSerializer),
            404: "Policy not found",
        },
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
        operation_description="Create policy and client atomic request",
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
        operation_description="Upload policy from excel sheet",
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="The file to upload",
            )
        ],
        responses={400: "Bad Request", 201: "Resource created successfully"},
    )
    def post(self, request, source):
        try:
            file_obj = request.data.get("file")
            if file_obj is None:
                return HTTPResponse.error(message="File is missing in the request.")

            if source == "bordrex":
                upload_clients_and_policies(
                    file_obj, CLIENT_COLUMNS_BORDREX, POLICY_COLUMNS_BORDREX
                )
            elif source == "guardrisk":
                upload_clients_and_policies(file_obj, CLIENT_COLUMNS, POLICY_COLUMNS)
            else:
                return HTTPResponse.success(
                    message="Incorrect report type",
                    status_code=status.HTTP_409_CONFLICT,
                )
            return HTTPResponse.success(
                message="Resource created successfully",
                status_code=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(e)
            return HTTPResponse.error(message=str(e))


# add dependencies
class PolicyDependenciesView(APIView):

    @swagger_auto_schema(
        operation_description="Add policy dependencies",
        request_body=DependantSerializer(
            many=True
        ),  # Update to accept a list of beneficiaries
        responses={
            201: openapi.Response("Created", DependantSerializer),
            400: "Bad Request",
        },
    )
    def post(self, request, policy_id):

        serializer = DependantSerializer(
            data=request.data,
            many=True,
            context={"request": request},
        )
        if serializer.is_valid():
            try:
                logger.info("Validated data: %s", serializer.validated_data)
                # Save the validated data to create a new Policy instance
                serializer.save(policy=policy_id)
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
        operation_description="Get policy dependencies",
        responses={
            201: openapi.Response("Request Successful", DependantSerializer),
            400: "Bad Request",
        },
    )
    def get(self, request, policy_id):
        dependencies = Dependant.objects.filter(policy_id=policy_id)

        return HTTPResponse.success(
            message="Request Successful",
            status_code=status.HTTP_200_OK,
            data=dependencies,
        )


# add policies
class PolicyBeneficiariesView(APIView):

    @swagger_auto_schema(
        operation_description="Add policy beneficiary",
        request_body=BeneficiarySerializer(
            many=True
        ),  # Update to accept a list of beneficiaries
        responses={
            201: openapi.Response("Created", BeneficiarySerializer),
            400: "Bad Request",
        },
    )
    def post(self, request, policy_id):

        serializer = BeneficiarySerializer(
            data=request.data,
            many=True,
            context={"request": request},
        )
        if serializer.is_valid():
            try:
                logger.info("Validated data: %s", serializer.validated_data)
                serializer.save(
                    policy=policy_id
                )  # Set the policy_id for each beneficiary
                return HTTPResponse.success(
                    message="Resources created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return HTTPResponse.error(message=str(e))
        else:
            return HTTPResponse.error(message=serializer.errors)

    @swagger_auto_schema(
        operation_description="Get policy policies",
        responses={
            201: openapi.Response("Request Successful", BeneficiarySerializer),
            400: "Bad Request",
        },
    )
    def get(self, request, policy_id):
        beneficiaries = Beneficiary.objects.filter(policy_id=policy_id)

        return HTTPResponse.success(
            message="Request Successful",
            status_code=status.HTTP_200_OK,
            data=beneficiaries,
        )


# policy payments


class CapturePaymentView(APIView):
    @swagger_auto_schema(
        request_body=PremiumPaymentSerializer,
        responses={201: PremiumPaymentSerializer()},
    )
    def post(self, request, policy_id):
        """
        Capture payment.
        """
        serializer = PremiumPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(policy=policy_id)
            return HTTPResponse.success(
                data=serializer.data, status_code=status.HTTP_201_CREATED
            )
        return HTTPResponse.error(
            message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(responses={200: PremiumPaymentSerializer(many=True)})
    def get(self, request, policy_id):
        """
        Get all policy payments.
        """
        payments = PremiumPayment.objects.filter(policy_id=policy_id)
        serializer = PremiumPaymentSerializer(payments, many=True)
        return HTTPResponse.success(
            data=serializer.data, status_code=status.HTTP_200_OK
        )


class UploadPaymentFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=MultiPartParser, responses={200: "File uploaded successfully."}
    )
    def put(self, request, format=None):
        """
        Upload payment file.
        """
        file_obj = request.FILES["file"]
        # Additional logic to parse and process the file
        return HTTPResponse.success(
            message="Payments successfully uploaded", status_code=status.HTTP_200_OK
        )
