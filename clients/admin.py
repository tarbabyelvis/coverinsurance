from django.contrib import admin
from clients.models import ClientDetails, ClientEmploymentDetails

@admin.register(ClientDetails)
class ClientDetailsAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'primary_id_number', 'email', 'phone_number']
    search_fields = ('first_name', 'last_name', 'primary_id_number', 'email', 'phone_number')

@admin.register(ClientEmploymentDetails)
class ClientEmploymentDetailsAdmin(admin.ModelAdmin):
    list_display = ['client', 'employer_name', 'job_title', 'sector']
    search_fields = ('client', 'employer_name', 'job_title', 'sector')
