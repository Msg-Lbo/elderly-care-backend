from django.contrib import admin
from django.utils.html import format_html
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'client', 'caregiver', 'status', 'service_time', 'address')
    list_filter = ('service_type', 'status', 'service_time')
    search_fields = ('client__user__username', 'caregiver__user__username', 'address')
    date_hierarchy = 'service_time'
    raw_id_fields = ('client', 'caregiver')
    list_per_page = 20
