from django.contrib import admin

from .models import Location, LoginLocation, LoginRecord


class LoginLocationInline(admin.TabularInline):
    model = LoginLocation
    extra = 0
    verbose_name = "Location Information"
    verbose_name_plural = "Location Information"

@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ("when", "user", "host", "service", "method", "fromhost", "result")
    list_filter = ("when", "service", "result")
    search_fields = ("service", "method", "host", "user", "fromhost")
    inlines = [LoginLocationInline]


