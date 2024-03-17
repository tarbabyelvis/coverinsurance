from jobs.serializers import JobsSerializer
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from jobs.services import credit_life
from marshmallow import ValidationError


class LifeCreditAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk report job",
        request_body=JobsSerializer,
        responses={200: "Request Successful", 409: "Conflict"},
    )
    def post(self, request, report_type):
        """
        Post Guardrisk report job.

        This endpoint allows you to post a Guardrisk report job.

        :param request: HTTP request object
        :param report_type: Type of report
        :return: HTTP response indicating success or failure
        """
        try:
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                credit_life(report_type, **serializer.validated_data)
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
