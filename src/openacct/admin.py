from django.contrib import admin

from .models    import (User, Project, UserProjectEvent, Account, System, Service,
                        Transaction, Job, StorageCommitment)


class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(User, UserAdmin)


class ProjectAdmin(admin.ModelAdmin):
    pass
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

