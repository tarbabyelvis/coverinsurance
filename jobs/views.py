from jobs.serializers import JobsSchema
from marshmallow import ValidationError
from core.http_response import HTTPResponse
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema


class LifeCreditAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Post Guardrisk report job",
        request_body={},
        responses={200: "Request Successful"},
    )
    def post(self, request, report_type):

        try:
            schema = JobsSchema()
            schema.load(dict(request.data))

        except ValidationError as e:
            print("Validation Error: ", e)
            return HTTPResponse.error(message=e.messages)
        except KeyError as e:
            print("Key Error: ", e)
            return HTTPResponse.error(message="Missing key in request data: " + str(e))
        except Exception as e:
            print("Error: ", e)
            return HTTPResponse.error(message=str(e))
