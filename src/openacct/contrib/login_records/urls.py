from django.urls import path

from .views import LoginRecordView

urlpatterns = [
    path("record/", LoginRecordView.as_view(), name="record-login"),
]
