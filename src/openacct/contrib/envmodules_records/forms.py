from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import EnvmodulesCommandRecord, EnvmodulesEventRecord


class EnvmodulesCommandRecordForm(forms.ModelForm):
    class Meta:
        model = EnvmodulesCommandRecord
        fields = [
            "when", "host", "user", "uuid", "command", "jobid", "account", "cluster"
        ]


class EnvmodulesEventRecordForm(forms.ModelForm):

    uuid = forms.CharField()

    class Meta:
        model = EnvmodulesEventRecord
        fields = ["mode", "auto", "module"]


    def clean(self):
        cd = super().clean()
        command_uuid = cd['command_uuid'] = cd.get('command_uuid', '')
        try:
            cd['caused_id'] = EnvmodulesCommandRecord.objects.get(
                name=command_uuid
            ).pk
            return cd
        except ObjectDoesNotExist:
            raise ValidationError("No match for the given Session UUID.")

    def save(self, commit=True):
        self.instance.caused_id = self.cleaned_data['caused_id']
        return super().save(commit=commit)
