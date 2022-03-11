from django.apps import AppConfig


class LoginRecordsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openacct.contrib.login_records"
    verbose_name = "Login History Records"
