from datetime import datetime

from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from core.http_response import HTTPResponse
from core.utils import CustomPagination
from policies.models import PremiumPayment
from policies.serializers import PolicyDetailSerializer, PremiumPaymentSerializer
from reports.utils import bordrex_report_util, generate_excel_report_util


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
        entity = request.GET.get("entity")
        # validate dates to make sure they are not null
        if not from_date or not to_date or not entity:
            return HTTPResponse.error(
                message="from and to dates and entity are required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policy_payments = fetch_active_policies_payments(entity, start_date=from_date, end_date=to_date)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(policy_payments, request)
            payments = PremiumPaymentSerializer(result_page, many=True).data
            report = bordrex_report_util(payments, from_date, to_date, entity=entity)
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
            print(e)
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
        entity = request.GET.get("entity", None)

        if not from_date or not to_date or not entity:
            return HTTPResponse.error(
                message="'from', 'to' and 'entity are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policies_payments = fetch_active_policies_payments(entity, start_date=from_date, end_date=to_date)

            # Serialize data
            serializer = PremiumPaymentSerializer(policies_payments, many=True)
            report = generate_excel_report_util(serializer.data, from_date, to_date, entity=entity)

            # Serve the Excel file as a response
            response = HttpResponse(
                report,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="exported_data.xlsx"'
            )
            return response

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def fetch_active_policies_payments(entity, start_date, end_date):
    # result = (
    #     PremiumPayment.objects.filter(
    #         payment_date__gte=start_date,
    #         payment_date__lte=end_date,
    #         policy__policy_status="A",
    #         policy__entity=entity,
    #         policy__policy_provider_type='Internal Credit Life'
    #     )
    #     .values('policy__policy_number')
    #     .annotate(
    #         total_amount=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
    #     ))
    # return list(result)
    return PremiumPayment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        policy__entity=entity,
        policy__policy_provider_type='Internal Credit Life'
    )
