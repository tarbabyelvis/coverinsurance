from django.http import HttpResponse
from rest_framework import status
from core.http_response import HTTPResponse
from core.utils import CustomPagination
from policies.models import Policy
from policies.serializers import PolicyDetailSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from datetime import datetime
import pandas as pd
from io import BytesIO
from reports.utils import bordrex_report_util


class BordrexReportView(APIView):
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="Bordrex Report",
        responses={
            200: openapi.Response("Success", PolicyDetailSerializer),
            404: "Policy not found",
        },
        manual_parameters=[
            openapi.Parameter(
                "from",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Start date",
                required=True,
            ),
            openapi.Parameter(
                "to",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="End date",
                required=True,
            ),
        ],
    )
    def get(self, request):
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)

        # validate dates to make sure they are not null
        if not from_date or not to_date:
            return HTTPResponse.error(
                message="from and to dates are required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policies = Policy.objects.filter(
                commencement_date__gte=from_date, commencement_date__lte=to_date
            )
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(policies, request)

            serializer = PolicyDetailSerializer(result_page, many=True).data
            report = bordrex_report_util(serializer)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={
                    "results": report,
                    "count": paginator.page.paginator.count if paginator.page else 0,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                },
            )

        except Exception as e:
            return HTTPResponse.error(
                message=str(e), status_code=status.HTTP_409_CONFLICT
            )


class BordrexExcelExportView(APIView):

    @swagger_auto_schema(
        operation_description="Export Bordrex report to Excel",
        manual_parameters=[
            openapi.Parameter(
                "from",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Start date",
                required=True,
            ),
            openapi.Parameter(
                "to",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="End date",
                required=True,
            ),
        ],
        responses={
            200: "Success",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def get(self, request):
        # Get data from the database
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="Both 'from' and 'to' dates are required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policies = Policy.objects.filter(
                commencement_date__gte=from_date, commencement_date__lte=to_date
            )

            # Serialize data
            serializer = PolicyDetailSerializer(policies, many=True)
            data = bordrex_report_util(serializer.data)

            # Convert data to DataFrame
            df = pd.DataFrame(data)

            # Write DataFrame to in-memory Excel file
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False)

            # Serve the Excel file as a response
            response = HttpResponse(
                excel_buffer.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="exported_data.xlsx"'
            )
            return response

        except Exception as e:
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
