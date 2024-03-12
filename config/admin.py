from django.contrib import admin
from .models import *

# @admin.register(PolicyName)
# class PolicyNameAdmin(admin.ModelAdmin):
#     list_display = ['name', "policy_type"]


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ["document_type", "category"]


@admin.register(Relationships)
class RelationshipsAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(IdDocumentType)
class IdDocumentTypeAdmin(admin.ModelAdmin):
    list_display = [
        "type_name",
    ]


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["agent_name", "entity_type", "phone_number", "email"]
    search_fields = ["agent_name", "entity_type", "phone_number", "email"]


# definition of additional claimfields
class ClaimFieldsInline(admin.TabularInline):
    model = ClaimFields
    extra = 1


class ClaimAdmin(admin.ModelAdmin):
    inlines = (ClaimFieldsInline,)


admin.site.register(ClaimType, ClaimAdmin)


class PolicyTypeFieldsInline(admin.TabularInline):
    model = PolicyTypeFields
    extra = 1


class PolicyFieldsAdmin(admin.ModelAdmin):
    inlines = (PolicyTypeFieldsInline,)


admin.site.register(PolicyName, PolicyFieldsAdmin)
