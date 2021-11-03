from django.contrib import admin

from .models    import (User, Project, UserProjectEvent, Account, System, Service,
                        Transaction, Job, StorageCommitment)

from .shortcuts import add_user_to_project, create_account


class ToggleActiveAdminMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'set_active' not in self.actions:
            self.actions.append('set_active')
        if 'set_inactive' not in self.actions:
            self.actions.append('set_inactive')
    
    def set_active(self, request, queryset):
        queryset.update(active=True)
    set_active.short_description = 'Mark selected items as active'

    def set_inactive(self, request, queryset):
        queryset.update(active=False)
    set_inactive.short_description = 'Mark selected items as inactive'


class ProjectMembershipInline(admin.TabularInline):
    model = User.projects.through
    extra = 0
    verbose_name = "Project Membership"
    verbose_name_plural = "Project Memberships"


class UserAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'realname', 'active', 'created')
    inlines = [ProjectMembershipInline]
    exclude = ('projects',)
admin.site.register(User, UserAdmin)


class ProjectAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            add_user_to_project(obj.pi, obj)
            create_account(obj)
    
    class AccountInline(admin.TabularInline):
        extra = 0
        model = Account
    
    inlines = [AccountInline, ProjectMembershipInline]
    list_display = ('name', 'description', 'ldap_group', 'active', 'created')

admin.site.register(Project, ProjectAdmin)


class UserProjectEventAdmin(admin.ModelAdmin):
    list_display = ('created', 'user', 'project', 'event_type')
admin.site.register(UserProjectEvent, UserProjectEventAdmin)


class AccountAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'project', 'active', 'created', 'expires')
admin.site.register(Account, AccountAdmin)


class SystemAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    class ServiceInline(admin.TabularInline):
        model = Service

    inlines = [ServiceInline]
    list_display = ('name', 'description', 'active', 'created')

admin.site.register(System, SystemAdmin)


class ServiceAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'system', 'charge_rate', 'units', 'active', 'created')
admin.site.register(Service, ServiceAdmin)


class TransactionAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        'created', 'active', 'tx_type', 'service', 'account', 'creator', 
        'amt_used', 'amt_charged'
    )
admin.site.register(Transaction, TransactionAdmin)


class JobAdmin(admin.ModelAdmin):
    pass
admin.site.register(Job, JobAdmin)


class StorageCommitmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(StorageCommitment, StorageCommitmentAdmin)

