from django.contrib import admin

from .models import (
    User,
    Project,
    UserProjectEvent,
    Account,
    System,
    Service,
    Transaction,
    Job,
    StorageCommitment,
)

from .shortcuts import add_user_to_project, create_account


class ToggleActiveAdminMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "set_active" not in self.actions:
            self.actions.append("set_active")
        if "set_inactive" not in self.actions:
            self.actions.append("set_inactive")

    def set_active(self, request, queryset):
        queryset.update(active=True)

    set_active.short_description = "Mark selected items as active"

    def set_inactive(self, request, queryset):
        queryset.update(active=False)

    set_inactive.short_description = "Mark selected items as inactive"


class ProjectMembershipInline(admin.TabularInline):
    model = User.projects.through
    extra = 0
    verbose_name = "Project Membership"
    verbose_name_plural = "Project Memberships"


@admin.register(User)
class UserAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = ("name", "realname", "active", "created")
    list_filter = ("active", "created")
    search_fields = ("name", "realname")
    inlines = [ProjectMembershipInline]
    exclude = ("projects",)


@admin.register(Project)
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
    list_display = ("name", "description", "ldap_group", "active", "created")
    list_filter = ("active", "created")
    search_fields = ("name", "description", "ldap_group")


@admin.register(UserProjectEvent)
class UserProjectEventAdmin(admin.ModelAdmin):
    list_display = ("created", "user", "project", "event_type")


@admin.register(Account)
class AccountAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = ("name", "project", "active", "created", "expires")


@admin.register(System)
class SystemAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    class ServiceInline(admin.TabularInline):
        model = Service

    inlines = [ServiceInline]
    list_display = ("name", "description", "active", "created")


@admin.register(Service)
class ServiceAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "system",
        "charge_rate",
        "units",
        "active",
        "created",
    )


@admin.register(Transaction)
class TransactionAdmin(ToggleActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "created",
        "active",
        "tx_type",
        "service",
        "account",
        "creator",
        "amt_used",
        "amt_charged",
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    class JobTxInline(admin.TabularInline):
        model = Job.transactions.through
        extra = 0
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
    
    list_display = (
        "jobid",
        "name",
        "account",
        "queued",
        "started",
        "completed",
    )
    list_filter = ("cluster", "account")
    search_fields = ("jobid", "name", "submitter", "account", "cluster")

    inlines = [JobTxInline]
    exclude = ("transactions",)


@admin.register(StorageCommitment)
class StorageCommitmentAdmin(admin.ModelAdmin):
    class StorCommTxInline(admin.TabularInline):
        model = StorageCommitment.transactions.through
        extra = 0
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    list_display = (
        "path",
        "filesystem",
        "dir_type",
        "project",
        "commitment",
        "allocated",
        "end_date",
    )
    list_filter = ("dir_type", "created", "allocated")
    search_fields = ("project", "filesystem", "path")
    inlines = [StorCommTxInline]
    exclude = ("transactions",)
