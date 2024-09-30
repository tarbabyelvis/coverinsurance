import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from django.db.models import Q
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.forms import DateField

from FinCover.settings import AWS_DOCUMENT_TENANT
from core import s3storage
from .models import *

logger = logging.getLogger(__name__)


def get_document_types():
    return list(DocumentType.objects.filter().values("id", "document_type"))


async def save_claim_document(
        claim, filename, doc_type, claim_file, file_metadata=None
):
    relative_path = "{tenant_name}/claims/{file_name}".format(
        tenant_name=AWS_DOCUMENT_TENANT, file_name=filename.replace(" ", "_")
    )
    actual_file_name = claim_file.name
    content_type = claim_file.content_type
    external_verification = None
    internally_verified = None
    expiration_date = None
    collection_date = None
    trust_level = None
    password = None
    try:
        if file_metadata is not None:
            print("File metadata: {}".format(file_metadata))
            if isinstance(file_metadata, dict):
                password = file_metadata.get("password", None)
            for meta in file_metadata:
                print(meta)
                print(type(meta))
                if meta["type"] == doc_type:
                    if meta.get("password") is not None:
                        password = meta["password"].get(actual_file_name, None)
                    external_verification = meta["external_verification"]
                    trust_level = meta["trust_level"]
                    collection_date = meta["collection_date"]
                    internally_verified = meta["internally_verified"]
    except Exception as e:
        print(f"Failed to to read file metadata {e}")

    if expiration_date is not None:
        expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    if collection_date is not None:
        collection_date = datetime.strptime(collection_date, "%Y-%m-%d").date()

    claim_doc = await ClaimDocument.objects.acreate(
        claim=claim,
        document_type_id=doc_type,
        document_name=filename,
        actual_name=actual_file_name,
        content_type=content_type,
        external_verification=external_verification,
        internally_verified=internally_verified,
        password=password,
        expiration_date=expiration_date,
        collection_date=collection_date,
        trust_level=trust_level,
    )
    await sync_to_async(claim_doc.document.save)(relative_path, claim_file)
    cld = await ClientClaimDocuments.objects.acreate(
        claim_id=claim.id,
        client_documents_id=claim_doc.id
    )
    print(cld)
    logger.info(
        "Claim document added :: {relative_path}".format(relative_path=claim_doc.document)
    )


def save_claim_document_blocking(claim, filename, doc_type, claim_file, content_type):
    relative_path = "{tenant_name}/claims/{file_name}".format(
        tenant_name=AWS_DOCUMENT_TENANT, file_name=filename.replace(" ", "_")
    )
    actual_file_name = claim_file.name
    external_verification = None
    internally_verified = None
    expiration_date = None
    collection_date = None
    trust_level = None

    if expiration_date is not None:
        expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    if collection_date is not None:
        collection_date = datetime.strptime(collection_date, "%Y-%m-%d").date()

    claim_doc = ClaimDocument.objects.create(
        client_number=claim.client_id_number,
        document_type_id=doc_type,
        document=filename,
        actual_name=actual_file_name,
        content_type=content_type,
        external_verification=external_verification,
        internally_verified=internally_verified,
        expiration_date=expiration_date,
        collection_date=collection_date,
        trust_level=trust_level,
    )
    print('saved claim doc {}'.format(claim_doc))
    claim_doc.document.save(relative_path, claim_file)
    ClientClaimDocuments.objects.create(
        claim_id=claim.id,
        client_documents_id=claim_doc.id
    )
    logger.info(
        "Claim document added :: {relative_path}".format(relative_path=claim_doc.document)
    )


def get_claim_documents(claim_id, filter_params=None):
    claim_docs = (ClientClaimDocuments.objects.filter(claim_id=claim_id).
    prefetch_related("client_claim_documents").values(
        "client_documents", "claim"
    ))
    print(f'claim docs {claim_docs}')
    pre_signed_documents = []
    for doc in claim_docs:
        filters = Q()
        if filter_params is not None:
            if filter_params.get("category") is not None:
                filters &= Q(document_type__category=filter_params.get("category"))
        else:
            filters &= ~Q(document_type__category="kyc_document")
        filters &= Q(id=doc["client_documents"], deleted_at__isnull=True)
        documents = (
            ClaimDocument.objects.order_by("-created")
            .filter(filters)
            .values(
                "id",
                "document_type__id",
                "document_type_category",
                "document",
                "document_name",
                "password",
                "created",
                "external_verification",
                "internally_verified",
                "expiration_date",
                "collection_date",
                "is_rejected",
            ))
        for document in documents:
            file_url = s3storage.create_pre_signed_url(document["document"])
            document["document"] = file_url
            document["document_name"] = document['document_name']
            document["previous"] = False
            pre_signed_documents.append(document)
    return pre_signed_documents


def get_kyc_documents(client_id_number):
    previous_documents = (
        ClientClaimDocuments.objects.order_by("-created")
        .filter(
            client_number=client_id_number,
            deleted_at__isnull=True,
            document_type__category="kyc_document",
        )
        .distinct("document_type__document_name")
        .values(
            "id",
            "client_number",
            "document_type__id",
            "document_type__document_name",
            "document_type__category",
            "document",
            "password",
            "created",
            "external_verification",
            "internally_verified",
            "expiration_date",
            "collection_date",
            "is_rejected",
        )
    )
    return previous_documents


def fetch_claims_needing_review():
    date_today = datetime.today().date()
    return Claim.objects.annotate(
        check_date=Cast(KeyTextTransform('debicheck_suspension_from', 'claim_details'), DateField())
    ).filter(claim_status='PAID', debicheck_suspension_from=date_today)
