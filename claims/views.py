import asyncio
import json
import logging
import time as itime
from datetime import datetime

import pdfkit
from asgiref.sync import sync_to_async, async_to_sync
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from claims.models import Claim
from config.models import DocumentType
from core.http_response import HTTPResponse
from core.utils import CustomPagination, standard_http_response
from drfasyncview import AsyncAPIView
from drfasyncview.authentication_class import AsyncAuthentication, AsyncIsAuthenticated
from .orm_queries import get_claim_documents, get_document_types, save_claim_document, save_claim_document_blocking
from .serializers import ClaimSerializer
from .services import process_claim_payment, process_claim, approve_claim, reactivate_debicheck, repudiate_claim

logger = logging.getLogger(__name__)


class ClaimCreateAPIView(APIView):
    # permission_classes = IsAuthenticated,
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="Create a new claim",
        request_body=ClaimSerializer,
        responses={
            201: openapi.Response("Created", ClaimSerializer),
            400: "Bad Request",
        },
    )
    def post(self, request):
        data = request.data
        raw_details = data["details"]
        print(f'create claim data: {data}')
        details = json.loads(raw_details)
        try:
            print("Getting File only")
            print(request.FILES)
        except Exception as e:
            print(f"Failed to process files: {e}")
        passwords = details.get("passwords", None)
        file_metadata = data.get("file_metadata", None)
        print(f'request data: {details}')
        claim_id = None
        serializer = ClaimSerializer(data=details)
        if serializer.is_valid():
            claim = serializer.save()
            claim_id = claim.id
        else:
            print(f'errors on creating claim: {serializer.errors}')
            return HTTPResponse.error(message=serializer.errors)

        doc_types = get_document_types()
        print(f'docs types: {doc_types}')
        print("Processing claim creation files")
        for k, vv in request.FILES.lists():
            password = None
            print("file", k, vv)
            if passwords is not None:
                password = passwords.get(k, None)
                print("\u001b[34mPassword:::  ", password, "\u001b[0m")
            doc_type = list(filter(lambda d: d["document_type"] == k, doc_types))
            print(f'document type: {doc_type}')
            time_str = itime.strftime("%Y%m%d%H%M%S%f")
            unique_id = 1
            for v in vv:
                try:
                    print(
                        f"Iterating through the files with file name: {v.name}"
                    )
                    file_extension = v.name.split(".")[-1]
                    filename = (
                            str(claim_id)
                            + "_"
                            + str(doc_type[0]["document_type"])
                            + "_"
                            + str(time_str)
                            + str(unique_id)
                            + "."
                            + str(file_extension)
                    )
                    unique_id += 1
                    print(f"The file name is: {filename}")
                    if password is not None:
                        if file_metadata is None:
                            file_metadata = {"password": password}
                        elif isinstance(password, dict):
                            for meta in list(
                                    filter(
                                        lambda d: d["type"] == doc_type[0]["id"],
                                        file_metadata,
                                    )
                            ):
                                meta["password"] = password
                        else:
                            file_metadata["password"] = password
                    try:
                        print("Trying to add documents")
                        async_to_sync(save_claim_document)(
                            claim,
                            filename,
                            doc_type[0]["id"],
                            v,
                            file_metadata=file_metadata,
                        )
                    except Exception as e:
                        print(str(e))
                except Exception as e:
                    print(f"Failed to add documents: {e}")
        print(f'after saving docs....')
        return HTTPResponse.success(
            message="Resource created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="Get all claims",
        responses={200: ClaimSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "claim_type",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Claim type ID",
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
        from_date = request.GET.get("from", None)
        to_date = request.GET.get("to", None)
        claim_type = request.GET.get("claim_type", None)
        query = request.GET.get("query", None)
        claims = Claim.objects.all()
        print(claims)
        if query:
            claims = claims.filter(
                Q(claimant_name__icontains=query)
                | Q(claimant_surname__icontains=query)
                | Q(claimant_id_number__icontains=query)
                | Q(claimant_email__icontains=query)
                | Q(claimant_phone__icontains=query)
                | Q(policy__insurer__name__icontains=query)
                | Q(policy__policy_number__icontains=query)
            )

        if claim_type is not None:
            claims = claims.filter(claim_type_id=claim_type)
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            claims = claims.filter(created__gte=from_date)

        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            claims = claims.filter(created__lte=to_date)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(claims, request)
        serializer = ClaimSerializer(result_page, many=True)
        claims_list = []
        for claim in serializer.data:
            print(f'claim {claim}')
            claims_list.append({
                "id": claim["id"],
                "name": claim["name"],
                "policy": claim["policy"],
                "claim_type": claim["claim_type"],
                "claim_document": claim["claim_document"],
                "claim_status": claim['claim_status'],
                "claim_assessed_by": claim['claim_assessed_by'],
                "claim_assessment_date": claim['claim_assessment_date'],
                "claim_amount": claim['claim_amount'],
                "claims_details": "",
                "submitted_date": claim['submitted_date'],
                "claim_paid_date": claim['claim_paid_date'],
                "claimant_name": claim['claimant_name'],
                "claimant_surname": claim['claimant_surname'],
                "claimant_id_number": claim['claimant_id_number'],
                "claimant_email": claim['claimant_email'],
                "claimant_phone": claim['claimant_phone'],
                "claimant_bank_name": claim['claimant_bank_name'],
                "claimant_bank_account_number": claim['claimant_bank_account_number'],
                "claimant_branch": claim['claimant_branch'],
                "claimant_branch_code": claim['claimant_branch_code'],
                "claimant_id_type": claim['claimant_id_type'],
                "claim_repudiated": claim['claim_repudiated'],
                "repudiated_date": claim['repudiated_date'],
                "repudiated_reason": claim['repudiated_reason']
            })
        return HTTPResponse.success(
            message="Resource retrieved successfully",
            status_code=status.HTTP_200_OK,
            data={
                "results": claims_list,
                "count": paginator.page.paginator.count if paginator.page else 0,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        )


class ClaimDetailAPIView(APIView):
    # permission_classes = (IsAuthenticated,

    @swagger_auto_schema(
        operation_description="Retrieve a specific Claim by ID",
        responses={
            200: openapi.Response("Success", ClaimSerializer),
            404: "Claim not found",
        },
    )
    def get(self, request, pk):
        try:
            policy = get_object_or_404(Claim, pk=pk)
            serializer = ClaimSerializer(policy)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data=serializer.data,
            )
        except Http404:
            return HTTPResponse.error(
                message="Claim not found", status_code=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        request_body=ClaimSerializer,
        responses={200: ClaimSerializer, 404: "Claim not found"},
        operation_description="Update a claim instance.",
    )
    def put(self, request, pk, format=None):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return HTTPResponse.error(
                message="Claim not found", status_code=status.HTTP_404_NOT_FOUND
            )
        data = request.data
        serializer = ClaimSerializer(claim, data=data)
        if serializer.is_valid():
            serializer.save()
            return HTTPResponse.success(
                data=serializer.data, status_code=status.HTTP_200_OK
            )
        return HTTPResponse.error(
            message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        request_body=ClaimSerializer,
        responses={200: ClaimSerializer, 404: "Claim not found"},
        operation_description="Update a claim instance.",
    )
    def patch(self, request, pk, format=None):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return HTTPResponse.error(
                message="Claim not found", status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ClaimSerializer(claim, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return HTTPResponse.success(
                data=serializer.data, status_code=status.HTTP_200_OK
            )
        return HTTPResponse.error(
            message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )


class ProcessClaimAPIView(APIView):
    # permission_classes = (IsAuthenticated,

    def get(self, request, pk):
        try:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            print(f'claim processing ...')
            process_claim(tenant_id, pk)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={},
            )
        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message="Request failed",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ApproveClaimAPIView(APIView):
    # permission_classes = (IsAuthenticated,

    def get(self, request, pk):
        try:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            print(f'claim approval ...')
            approve_claim(tenant_id, pk)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={},
            )
        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message="Request failed:: {}".format(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class RepudiateClaimAPIView(APIView):
    # permission_classes = (IsAuthenticated,

    def post(self, request, pk):
        try:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            data = request.data
            print(f'claim repudiation ...{data}')
            repudiation_reason = data['repudiation_reason']
            repudiated_by = data['repudiated_by']
            repudiate_claim(tenant_id, pk, repudiation_reason, repudiated_by)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={},
            )
        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message="Request failed:: {}".format(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ReceiptClaimAPIView(APIView):
    # permission_classes = (IsAuthenticated,

    def post(self, request, pk):
        try:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            data = request.data
            print(f'receipt claim ...{data}')
            claim_amount = data['amount']
            payment_date = data['paymentDate']
            notes = data['notes']
            receipt_number = data['receiptNumber']
            receipted_by = data['receiptedBy']
            payment_method = data['paymentMethod']
            process_claim_payment(tenant_id=tenant_id,
                                  claim_id=pk,
                                  claim_amount=claim_amount,
                                  payment_date=payment_date,
                                  notes=notes,
                                  receipt_number=receipt_number,
                                  receipted_by=receipted_by,
                                  payment_method=payment_method)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={},
            )
        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message="Request failed:: {}".format(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ReactivateDebicheckAPIView(APIView):
    # permission_classes = (IsAuthenticated,

    def post(self, request, pk):
        try:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            data = request.data
            print(f'reactivate debicheck ...{data}')
            reactivate_debicheck(tenant_id, pk)
            return HTTPResponse.success(
                message="Request Successful",
                status_code=status.HTTP_200_OK,
                data={},
            )
        except Exception as e:
            print(e)
            return HTTPResponse.error(
                message="Request failed:: {}".format(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class AddDocuments(AsyncAPIView):
    # authentication_classes = [AsyncAuthentication]
    # permission_classes = [
    #     AsyncIsAuthenticated,
    # ]

    async def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(
                {"error": "missing parameters"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            print("Client request saving new Document")
            print(f'request:: {request.data}')
            raw_details = request.data["details"]
            additional_details = request.data.get("additional_details", None)
            details = json.loads(raw_details)
            print("------------Printing raw details coming----------")
            print(raw_details)
            print(additional_details)
            claim_id = details["claim_id"]
            passwords = details.get("passwords", None)
            claim = await Claim.objects.aget(id=claim_id)
            # Get all document types
            doc_types = await sync_to_async(get_document_types, thread_sensitive=True)()
            # id => 23 '23-3446' plit - [0]
            for k, v in request.data.items():
                password = None
                if k.isdigit():
                    print(k, v)
                    doc_type = list(filter(lambda d: d["id"] == int(k), doc_types))
                    time_str = itime.strftime("%Y%m%d%H%M%S")

                    file_extension = v.name.split(".")[-1]
                    filename = (
                            str(claim.client_id_number)
                            + "_"
                            + str(doc_type[0]["name"])
                            + "_"
                            + str(time_str)
                            + "."
                            + str(file_extension)
                    )
                    if passwords is not None:
                        password = passwords.get(k, None)
                    try:
                        print("Trying to add documents")
                        await asyncio.create_task(
                            save_claim_document(
                                claim,
                                filename,
                                doc_type[0]["id"],
                                v,
                                {"password": password},
                            )
                        )
                    except Exception as e:
                        logger.info(str(e))
            return Response({"id": claim.id}, status=status.HTTP_200_OK)


class GetClaimDocumentsView(APIView):
    # permission_classes = (IsAuthenticated,

    def get(self, request, *args, **kwargs):
        # tenant_id = str(request.tenant).replace("-", "_")
        tenant_id = "fin_za_onlineloans"
        claim_id = self.kwargs["pk"]
        response_object = standard_http_response()
        try:
            claim = Claim.objects.get(id=claim_id)
            data = get_claim_documents(claim_id, None, claim.client_id_number)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            response_object["message"] = "Error retrieving claim documents"
            response_object["error"] = str(e)
            return Response(response_object, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddDocTemplates(AsyncAPIView):
    # authentication_classes = [AsyncAuthentication]
    # permission_classes = [
    #     AsyncIsAuthenticated,
    # ]

    async def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(
                {"error": "missing parameters"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # tenant_id = str(request.tenant).replace("-", "_")
            tenant_id = "fin_za_onlineloans"
            claim_id = request.data.get("claim_id", None)
            templates = request.data.get("templates", None)
            claim = await Claim.objects.aget(id=int(claim_id))
            if claim is None or templates is None:
                return Response(
                    {"error": "missing parameters"}, status=status.HTTP_400_BAD_REQUEST
                )
            await save_template_documents(claim, templates)
            return Response("success", status=status.HTTP_200_OK)


async def save_template_documents(claim, templates):
    print(f"Templates: {templates}")
    try:
        if templates is not None:
            for template in templates:
                document_code = template["code"]
                doc_type = await DocumentType.objects.aget(code=document_code)
                dc_type = doc_type.id
                today = datetime.now()
                today = today.strftime("%Y%m%d%H%M")
                print(f"Attempting to save template doc with doc type :{dc_type}")
                filename = today + ".pdf"
                await sync_to_async(save_template_document, thread_sensitive=True)(
                    template=template,
                    doc_type=dc_type,
                    filename=filename,
                    claim=claim,
                )
    except Exception as e:
        print(f"Something went wrong saving template doc: {e}")


def save_template_document(template, doc_type, filename, claim):
    options = {
        "margin-bottom": "0.55in",
        "margin-top": "0.55in",
        "margin-left": "0.75in",
        "margin-right": "0.75in",
        "footer-right": "[page] of [topage]",
        "footer-font-size": 10,
    }
    html = template["data"]
    print("The template is here")
    print(html)
    print("After template")
    pdfkit.from_string(html, "/tmp/" + filename, options)
    fs = FileSystemStorage("/tmp")
    with fs.open(filename) as pdf:
        print("Saving template doc in pdf")
        try:
            print("Trying to add documents")
            save_claim_document_blocking(
                claim, filename, doc_type, pdf, "application/pdf"
            )
            print("After saving template document")
        except Exception as e:
            print(f"Failed to save document: {e}")
