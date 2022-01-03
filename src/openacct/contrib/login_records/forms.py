from django import forms

from .models import LoginRecord


class LoginRecordForm(forms.ModelForm):
    class Meta:
        model = LoginRecord
        fields = ["when", "host", "service", "method", "user", "fromhost"]
