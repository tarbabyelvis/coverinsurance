from collections import defaultdict
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Value, DecimalField
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from clients.models import ClientDetails
from core.http_response import HTTPResponse
from core.utils import CustomPagination
from policies.models import PremiumPayment, Policy
from policies.serializers import PolicyDetailSerializer
from reports.services import fetch_quarterly_bordraux_summary, generate_quarterly_excel_report, fetch_policies, \
    summarize_policies, generate_policies_excel_report, fetch_claims, summarize_claims, generate_claims_excel_report, \
    summarize_clients, generate_clients_excel_report
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
            policy_payments = fetch_active_policies_payments(entity, start_date=from_date, end_date=to_date)
            page_number = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 20)
            paginator = Paginator(policy_payments, page_size)

            paginated_payments = paginator.page(page_number)
            report = bordrex_report_util(paginated_payments, from_date, to_date, entity=entity)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={
                    "results": report,
                    "count": paginator.count if paginator.page else 0,
                    "next": paginated_payments.has_next() and paginated_payments.next_page_number() or None,
                    "previous": paginated_payments.has_previous() and paginated_payments.
                    previous_page_number() or None,
                },
            )

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=str(e), status_code=status.HTTP_409_CONFLICT
            )


class BordrexExcelExportView(APIView):
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
            policy_payments = fetch_active_policies_payments(entity, start_date=from_date, end_date=to_date)
            page_number = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 20)
            paginator = Paginator(policy_payments, page_size)

            paginated_payments = paginator.page(page_number)
            report = bordrex_report_util(paginated_payments, from_date, to_date, entity=entity)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={
                    "results": report,
                    "count": paginator.count if paginator.page else 0,
                    "next": paginated_payments.has_next() and paginated_payments.next_page_number() or None,
                    "previous": paginated_payments.has_previous() and paginated_payments.
                    previous_page_number() or None,
                },
            )

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=str(e), status_code=status.HTTP_409_CONFLICT
            )


def fetch_active_policies_payments(entity, start_date, end_date):
    payment_criteria = Q(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        policy__entity=entity,
        policy__policy_provider_type='Internal Credit Life'
    )

    # Define the query criteria for policies
    policy_criteria = Q(
        entity=entity,
        policy_provider_type='Internal Credit Life',
        policy_status='A'
    )
    payments = PremiumPayment.objects.filter(payment_criteria).select_related('policy__client').values(
        'policy_id',
        'policy__policy_details'
    ).annotate(
        premium_paid=Sum('amount'),
        premium_annotated=F('policy__premium'),
        policy_number_annotated=F('policy__policy_number'),
        division=F('policy__business_unit'),
        risk_identifier_annotated=F('policy__policy_details__risk_identifier'),
        scheme_sub_annotated=F('policy__sub_scheme'),
        commencement_date_annotated=F('policy__commencement_date'),
        expiry_date_annotated=F('policy__expiry_date'),
        policy_term_annotated=F('policy__policy_term'),
        premium_frequency_annotated=F('policy__premium_frequency'),
        sum_insured_annotated=F('policy__sum_insured'),
        current_outstanding_balance_annotated=F('policy__policy_details__current_outstanding_balance'),
        installment_amount_annotated=F('policy__policy_details__installment_amount'),
        last_name=F('policy__client__last_name'),
        first_name=F('policy__client__first_name'),
        primary_id_number=F('policy__client__primary_id_number'),
        gender=F('policy__client__gender'),
        date_of_birth=F('policy__client__date_of_birth'),
        date_of_death=F('policy__client__date_of_death'),
        address_street=F('policy__client__address_street'),
        address_town=F('policy__client__address_town'),
        address_province=F('policy__client__address_province'),
        postal_code=F('policy__client__postal_code'),
        phone_number=F('policy__client__phone_number')
    )
    policy_ids_with_payments = payments.values_list('policy_id', flat=True)
    policies_without_payments = Policy.objects.filter(policy_criteria).exclude(
        id__in=policy_ids_with_payments).annotate(
        premium_paid=Value(0, output_field=DecimalField()),
        administrator_identifier=F('entity'),
        policy_number_annotated=F('policy_number'),
        division=F('business_unit'),
        scheme_sub_annotated=F('sub_scheme'),
        commencement_date_annotated=F('commencement_date'),
        expiry_date_annotated=F('expiry_date'),
        premium_annotated=F('premium'),
        policy_term_annotated=F('policy_term'),
        premium_frequency_annotated=F('premium_frequency'),
        sum_insured_annotated=F('sum_insured'),
        current_outstanding_balance_annotated=F('policy_details__current_outstanding_balance'),
        risk_identifier_annotated=F('policy_details__risk_identifier'),
        installment_amount_annotated=F('policy_details__installment_amount'),
        last_name=F('client__last_name'),
        first_name=F('client__first_name'),
        primary_id_number=F('client__primary_id_number'),
        gender=F('client__gender'),
        date_of_birth=F('client__date_of_birth'),
        date_of_death=F('client__date_of_death'),
        address_street=F('client__address_street'),
        address_town=F('client__address_town'),
        address_province=F('client__address_province'),
        postal_code=F('client__postal_code'),
        phone_number=F('client__phone_number')
    ).values()
    payment_map = defaultdict(lambda: {
        "policy_id": None,
        "premium_annotated": None,
        "premium_paid": 0,
        "division": None,
        "risk_identifier_annotated": None,
        "scheme_sub_annotated": None,
        "commencement_date_annotated": None,
        "expiry_date_annotated": None,
        "policy_term_annotated": None,
        "premium_frequency_annotated": None,
        "sum_insured_annotated": None,
        "current_outstanding_balance_annotated": None,
        "installment_amount_annotated": None,
        "last_name": None,
        "first_name": None,
        "primary_id_number": None,
        "gender": None,
        "date_of_birth": None,
        "date_of_death": None,
        "address_street": None,
        "address_town": None,
        "address_province": None,
        "postal_code": None,
        "phone_number": None,
    })
    for payment in payments:
        policy_id = payment['policy_id']
        payment_map[policy_id]["premium_annotated"] = payment['premium_annotated']
        payment_map[policy_id]["policy_number_annotated"] = payment['policy_number_annotated']
        payment_map[policy_id]["policy_id"] = policy_id
        payment_map[policy_id]["premium_paid"] += payment['premium_paid']
        payment_map[policy_id]["division"] = payment['division']
        payment_map[policy_id]["risk_identifier_annotated"] = payment['risk_identifier_annotated']
        payment_map[policy_id]["scheme_sub_annotated"] = payment['scheme_sub_annotated']
        payment_map[policy_id]["commencement_date_annotated"] = payment['commencement_date_annotated']
        payment_map[policy_id]["expiry_date_annotated"] = payment['expiry_date_annotated']
        payment_map[policy_id]["policy_term_annotated"] = payment['policy_term_annotated']
        payment_map[policy_id]["premium_frequency_annotated"] = payment['premium_frequency_annotated']
        payment_map[policy_id]["sum_insured_annotated"] = payment['sum_insured_annotated']
        payment_map[policy_id]["current_outstanding_balance_annotated"] = payment[
            'current_outstanding_balance_annotated']
        payment_map[policy_id]["installment_amount_annotated"] = payment['installment_amount_annotated']
        payment_map[policy_id]["last_name"] = payment['last_name']
        payment_map[policy_id]["first_name"] = payment['first_name']
        payment_map[policy_id]["primary_id_number"] = payment['primary_id_number']
        payment_map[policy_id]["gender"] = payment['gender']
        payment_map[policy_id]["date_of_birth"] = payment['date_of_birth']
        payment_map[policy_id]["date_of_death"] = payment['date_of_death']
        payment_map[policy_id]["address_street"] = payment['address_street']
        payment_map[policy_id]["address_town"] = payment['address_town']
        payment_map[policy_id]["address_province"] = payment['address_province']
        payment_map[policy_id]["postal_code"] = payment['postal_code']
        payment_map[policy_id]["phone_number"] = payment['phone_number']

    return list(payment_map.values()) + list(policies_without_payments)


class ClientExcelExportView(APIView):

    @swagger_auto_schema(
        operation_description="Export Client report to Excel",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policies_payments = fetch_active_policies_payments(start_date=from_date, end_date=to_date)
            report = generate_excel_report_util(policies_payments, from_date, to_date)

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


class BordrauxQuarterlyReportView(APIView):

    @swagger_auto_schema(
        operation_description="Export Bordrex quarterly report",
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
            data = fetch_quarterly_bordraux_summary(from_date, to_date, entity)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=data,
            )

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=str(e), status_code=status.HTTP_409_CONFLICT
            )


class BordrauxQuarterlyExportReportView(APIView):

    @swagger_auto_schema(
        operation_description="Export Bordrex quarterly report to Excel",
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
            report = generate_quarterly_excel_report(from_date, to_date, entity)

            response = HttpResponse(
                report,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="exported_data_quarterly.xlsx"'
            )
            return response

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PoliciesSummaryReportView(APIView):

    @swagger_auto_schema(
        operation_description="Policies summary report",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="'from', 'to' are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policy_type = request.GET.get("policy_type", None)
            query = request.GET.get("query", None)
            policies = fetch_policies(policy_type, from_date, to_date, query)
            data = summarize_policies(policies)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=data,
            )

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PoliciesSummaryReportExcelView(APIView):

    @swagger_auto_schema(
        operation_description="Policies summary report to excel",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="'from', 'to' are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policy_type = request.GET.get("policy_type", None)
            query = request.GET.get("query", None)
            report = generate_policies_excel_report(policy_type, from_date, to_date, query)
            response = HttpResponse(
                report,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="policies_summary.xlsx"'
            )
            return response

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClaimsSummaryReportView(APIView):

    @swagger_auto_schema(
        operation_description="Claims summary report",
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
        print('fetching claims....')
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        claim_type = request.GET.get("claim_type", None)
        query = request.GET.get("query", None)
        print(f'query: {query} from_date: {from_date} to_date: {to_date} claim_type: {claim_type}')

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="'from', 'to' are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

            claims = fetch_claims(claim_type, from_date, to_date, query)
            data = summarize_claims(claims)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=data,
            )

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClaimsSummaryReportExcelView(APIView):

    @swagger_auto_schema(
        operation_description="Policies summary report to excel",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="'from', 'to' are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            policy_type = request.GET.get("policy_type", None)
            query = request.GET.get("query", None)
            report = generate_claims_excel_report(policy_type, from_date, to_date, query)
            response = HttpResponse(
                report,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="claims_summary.xlsx"'
            )
            return response

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientsSummaryReportView(APIView):

    @swagger_auto_schema(
        operation_description="Clients summary report",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        query = request.GET.get("query", None)

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="'from', 'to' are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            clients = fetch_clients(from_date, to_date, query)
            data = summarize_clients(clients)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=data,
            )

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientsSummaryReportExcelView(APIView):

    @swagger_auto_schema(
        operation_description="Clients summary report to excel",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        query = request.GET.get("query", None)

        if not from_date or not to_date:
            return HTTPResponse.error(
                message="'from', 'to' are required .",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            report = generate_clients_excel_report(from_date, to_date, query)
            response = HttpResponse(
                report,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                'attachment; filename="clients_summary.xlsx"'
            )
            return response

        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message=f"An error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def fetch_clients(from_date, to_date, query):
    clients = ClientDetails.objects.all()
    if query:
        clients = clients.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(external_id__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(primary_id_number__icontains=query)
        )

    if from_date:
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        clients = clients.filter(created__gte=from_date)

    if to_date:
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        clients = clients.filter(created__lte=to_date)
    return clients
