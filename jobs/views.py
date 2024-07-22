from drf_yasg.utils import swagger_auto_schema
from marshmallow import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.http_response import HTTPResponse
from core.utils import get_current_schema
from jobs.serializers import JobsSerializer
from jobs.services import daily_job_postings, monthly_job_postings, fetch_and_process_fin_connect_data


class DailyJobPostingAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk daily report job",
        request_body=JobsSerializer,
        responses={200: "Request Successful", 409: "Conflict"},
    )
    def post(self, request):
        """
        Post Guardrisk report job.

        This endpoint allows you to post a Guardrisk report job.

        :param request: HTTP request object
        :return: HTTP response indicating success or failure
        """
        try:
            current_schema = get_current_schema()
            print(f'current_schema: {current_schema}')
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                daily_job_postings(**serializer.validated_data)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            print("Validation Error: ", e)
            return HTTPResponse.error(
                message=e.messages,
                status_code=status.HTTP_409_CONFLICT,
            )
        except KeyError as e:
            print("Key Error: ", e)
            return HTTPResponse.error(
                message="Missing key in request data: " + str(e),
                status_code=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            print("Error: ", e)
            return HTTPResponse.error(
                message=str(e),
                status_code=status.HTTP_409_CONFLICT,
            )


class MonthlyJobPostingsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk monthly report job",
        request_body=JobsSerializer,
        responses={200: "Request Successful", 409: "Conflict"},
    )
    def post(self, request):
        """
        Post Guardrisk report job.

        This endpoint allows you to post a Guardrisk report job.

        :param request: HTTP request object
        :return: HTTP response indicating success or failure
        """
        try:
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                monthly_job_postings(**serializer.validated_data)
                return HTTPResponse.success(
                    message="Request Successful",
                    status_code=status.HTTP_200_OK,
                )
        except ValidationError as e:
            print("Validation Error: ", e)
            return HTTPResponse.error(
                message=e.messages,
                status_code=status.HTTP_409_CONFLICT,
            )
        except KeyError as e:
            print("Key Error: ", e)
            return HTTPResponse.error(
                message="Missing key in request data: " + str(e),
                status_code=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            print("Error: ", e)
            return HTTPResponse.error(
                message=str(e),
                status_code=status.HTTP_409_CONFLICT,
            )


class FetchFinConnectDataAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Fetch Finconnect data job",
        request_body=JobsSerializer,
        responses={200: "Request Successful", 409: "Conflict"},
    )
    def post(self, request):
        """
        Fetch Finconnect data job.

        This endpoint allows you fetch finconnect data.

        :param request: HTTP request object
        :return: HTTP response indicating success or failure
        """
        try:
            request_data = request.data
            serializer = JobsSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                fin_organization_id = str(request.GET.get('fin_organization_id')).replace("-", "_")
                fetch_and_process_fin_connect_data(**serializer.validated_data, fineract_org_id=fin_organization_id)
                return HTTPResponse.success(
                    message="Request Successful",
                    status_code=status.HTTP_200_OK,
                )
        except ValidationError as e:
            print("Validation Error: ", e)
            return HTTPResponse.error(
                message=e.messages,
                status_code=status.HTTP_409_CONFLICT,
            )
        except KeyError as e:
            print("Key Error: ", e)
            return HTTPResponse.error(
                message="Missing key in request data: " + str(e),
                status_code=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            print("Error: ", e)
            return HTTPResponse.error(
                message=str(e),
                status_code=status.HTTP_409_CONFLICT,
            )
