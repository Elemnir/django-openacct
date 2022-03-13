from django.contrib import admin

from .models import EmailTemplate, Request

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "submitted", 
        "description", 
        "requester", 
        "status", 
        "review_link"
    )
    list_filter = (
        "status",
        "submitted",
    )
    search_fields = (
        "requester",
        "description",
    )
