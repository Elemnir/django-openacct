from django.contrib import admin

from .models    import (User, Project, UserProjectEvent, Account, System, Service,
                        Transaction, Job, StorageCommitment)

from .shortcuts import add_user_to_project, create_account


class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(User, UserAdmin)


class ProjectAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            add_user_to_project(obj.pi, obj)
            create_account(obj)

admin.site.register(Project, ProjectAdmin)


class UserProjectEventAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProjectEvent, UserProjectEventAdmin)


class AccountAdmin(admin.ModelAdmin):
    pass
admin.site.register(Account, AccountAdmin)


class SystemAdmin(admin.ModelAdmin):
    pass
admin.site.register(System, SystemAdmin)


class ServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Service, ServiceAdmin)


class TransactionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Transaction, TransactionAdmin)


class JobAdmin(admin.ModelAdmin):
    pass
admin.site.register(Job, JobAdmin)


class StorageCommitmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(StorageCommitment, StorageCommitmentAdmin)

