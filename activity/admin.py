from django.contrib import admin
from .models import Activity, ActivityRegistration

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'registration_count')
    list_filter = ('start_time', 'end_time')
    search_fields = ('title', 'content')
    date_hierarchy = 'start_time'
    
    def registration_count(self, obj):
        return obj.registrations.count()
    registration_count.short_description = '报名人数'

@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'user', 'registered_at')
    list_filter = ('registered_at',)
    search_fields = ('activity__title', 'user__username')
    date_hierarchy = 'registered_at' 