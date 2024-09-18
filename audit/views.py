from datetime import datetime

from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from audit.models import AuditTrail
from audit.serializers import AuditTrailSerializer
from core.http_response import HTTPResponse


class ClaimAuditAPIView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        pass
        # print('in audit logs..')
        # from_date = request.GET.get("from", None)
        # to_date = request.GET.get("to", None)
        # audit_logs = AuditTrail.objects.filter(
        #     Q(model_name='Claim',
        #       commencement_date__range=(start_date, end_date)
        #       )
        # )
        # if query:
        #     audit_logs = audit_logs.filter(
        #         Q(claimant_name__icontains=query),
        #                  | Q(claimant_surname__icontains=query)
        #                  | Q(claimant_id_number__icontains=query)
        #                  | Q(claimant_email__icontains=query)
        #                  | Q(claimant_phone__icontains=query)
        #                  | Q(policy__insurer__name__icontains=query)
        #                  | Q(policy__policy_number__icontains=query)
        #     )
        #
        #     if claim_type is not None:
        #         audit_logs = audit_logs.filter(claim_type_id=claim_type)
        #     if from_date:
        #         from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        #         audit_logs = audit_logs.filter(created__gte=from_date)
        #
        #     if to_date:
        #         to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        #         audit_logs = audit_logs.filter(created__lte=to_date)
        #     paginator = self.pagination_class()
        #     result_page = paginator.paginate_queryset(audit_logs, request)
        #     serializer = AuditTrailSerializer(result_page, many=True)
        #     claims_logs = []
        #     for claim in serializer.data:
        #         print(f'claim {claim}')
        #         claims_logs.append({
        #             "id": claim["id"],
        #             "name": claim["name"],
        #             "policy": claim["policy"],
        #             "claim_type": claim["claim_type"],
        #             "claim_document": claim["claim_document"],
        #             "claim_status": claim['claim_status'],
        #             "claim_assessed_by": claim['claim_assessed_by'],
        #             "claim_assessment_date": claim['claim_assessment_date'],
        #             "claim_amount": claim['claim_amount'],
        #             "claims_details": "",
        #             "submitted_date": claim['submitted_date'],
        #             "claim_paid_date": claim['claim_paid_date'],
        #             "claimant_name": claim['claimant_name'],
        #             "claimant_surname": claim['claimant_surname'],
        #             "claimant_id_number": claim['claimant_id_number'],
        #             "claimant_email": claim['claimant_email'],
        #             "claimant_phone": claim['claimant_phone'],
        #             "claimant_bank_name": claim['claimant_bank_name'],
        #             "claimant_bank_account_number": claim['claimant_bank_account_number'],
        #             "claimant_branch": claim['claimant_branch'],
        #             "claimant_branch_code": claim['claimant_branch_code'],
        #             "claimant_id_type": claim['claimant_id_type'],
        #             "claim_repudiated": claim['claim_repudiated'],
        #             "repudiated_date": claim['repudiated_date'],
        #             "repudiated_reason": claim['repudiated_reason']
        #         })
        #     return HTTPResponse.success(
        #         message="Resource retrieved successfully",
        #         status_code=status.HTTP_200_OK,
        #         data={
        #             "results": claims_logs,
        #             "count": paginator.page.paginator.count if paginator.page else 0,
        #             "next": paginator.get_next_link(),
        #             "previous": paginator.get_previous_link(),
        #         },
        #     )
