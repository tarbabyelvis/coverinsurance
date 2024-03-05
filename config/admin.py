from django.contrib import admin
from .models import *

@admin.register(PolicyName)
class PolicyNameAdmin(admin.ModelAdmin):
    list_display = ['name', "policy_type"]

@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ['name',]

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'category']

@admin.register(Relationships)
class RelationshipsAdmin(admin.ModelAdmin):
    list_display = ['name',]

@admin.register(IdDocumentType)
class IdDocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['type_name',]


