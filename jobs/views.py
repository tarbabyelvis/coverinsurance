from datetime import datetime, timedelta

from drf_yasg.utils import swagger_auto_schema
from marshmallow import ValidationError
from rest_framework import status
from rest_framework.views import APIView

from core.http_response import HTTPResponse
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
            tenant_id = str(request.tenant).replace("-", "_")
            print('tenant_id', tenant_id)
            if tenant_id == 'fin_za':
                data = request.data
                print(f'data {data}')
                if data:
                    serializer = JobsSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        daily_job_postings(**serializer.validated_data)
                        return HTTPResponse.success(
                            message="Request Successful",
                            status_code=status.HTTP_200_OK,
                        )
                    return HTTPResponse.error(
                        message="Invalid request data",
                        status_code=status.HTTP_409_CONFLICT,
                    )

                daily_job_postings()
                return HTTPResponse.success(
                    message="Request Successful",
                    status_code=status.HTTP_200_OK,
                )
            else:
                print('in wrong tenant')
                return HTTPResponse.error(
                    message="Invalid request tenant",
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
            tenant_id = str(request.tenant).replace("-", "_")
            fin_organization_id = str(request.GET.get('fin_organization_id')).replace("-", "_")
            print(f'tenant {tenant_id} fetching from fin organization {fin_organization_id}')
            data = request.data
            if data:
                serializer = JobsSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    pass
                    fetch_and_process_fin_connect_data(
                        **serializer.validated_data,
                        fineract_org_id=fin_organization_id)
                    return HTTPResponse.success(
                        message="Fineract fetch data request Successful",
                        status_code=status.HTTP_200_OK,
                    )
                return HTTPResponse.error(
                    message="Invalid request data",
                    status_code=status.HTTP_409_CONFLICT,
                )
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            print(f'fetching from fineract data from {yesterday}  to {yesterday}')
            fetch_and_process_fin_connect_data(
                start_date=yesterday,
                end_date=yesterday,
                fineract_org_id=fin_organization_id)
            return HTTPResponse.success(
                message="Fineract fetch data request Successful",
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
