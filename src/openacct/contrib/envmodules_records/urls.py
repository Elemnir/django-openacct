from django.urls import path

from .views import EnvmodulesCommandRecordView, EnvmodulesEventRecordView

urlpatterns = [
    path("record_command/", EnvmodulesCommandRecordView.as_view(), name="record-command"),
    path("record_event/", EnvmodulesEventRecordView.as_view(), name="record-event"),
]
