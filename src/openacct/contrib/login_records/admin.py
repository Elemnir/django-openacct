from django.contrib import admin

from .models import LoginRecord


class LoginRecordAdmin(admin.ModelAdmin):
    pass


admin.site.register(LoginRecord, LoginRecordAdmin)
