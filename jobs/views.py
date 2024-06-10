from jobs.serializers import JobsSerializer
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from jobs.services import credit_life
from marshmallow import ValidationError


class LifeCreditDailyAPIView(APIView):
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
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                credit_life_daily(**serializer.validated_data)
                # credit_life_daily() TODO to use when all tests are fine
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


class LifeCreditAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk report job",
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
                credit_life(**serializer.validated_data)
                # credit_life()
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


class FuneralCoverDailyAPIView(APIView):
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
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                funeral_cover_daily(**serializer.validated_data)
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


class FuneralCoverAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk funeral cover report job",
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
                funeral_cover(**serializer.validated_data)
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


class LifeClaimsDailyAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk daily claims report job",
        request_body=JobsSerializer,
        responses={200: "Request Successful", 409: "Conflict"},
    )
    def post(self, request):
        """
        Post Guardrisk report job.

        This endpoint allows you to post a Guardrisk claims report job.

        :param request: HTTP request object
        :return: HTTP response indicating success or failure
        """
        try:
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                life_claims_daily(**serializer.validated_data)
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


class LifeClaimsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Post Guardrisk daily report job",
        request_body=JobsSerializer,
        responses={200: "Request Successful", 409: "Conflict"},
    )
    def post(self, request):
        """
        Post Guardrisk report job.

        This endpoint allows you to post a Guardrisk claims report job.

        :param request: HTTP request object
        :return: HTTP response indicating success or failure
        """
        try:
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                life_claims(**serializer.validated_data)
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
