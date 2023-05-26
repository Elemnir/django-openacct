from django.contrib import admin

from .models import EnvmodulesCommandRecord, EnvmodulesEventRecord


@admin.register(EnvmodulesCommandRecord)
class EnvmodulesCommandRecordAdmin(admin.ModelAdmin):
    class EnvmodulesEventRecordInline(admin.TabularInline):
        model = EnvmodulesEventRecord
        extra = 0
        verbose_name = "Environment Module Event"
        verbose_name_plural = "Environment Module Events"

    list_display = (
        "when", "host", "user", "command", "cluster", "account", "jobid"
    )
    list_filter = ("when", "cluster", "account")
    search_fields = ("host", "user", "command", "jobid")

    inlines = [EnvmodulesEventRecordInline]
