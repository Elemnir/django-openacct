from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from openacct.contrib.token_auth.mixins import TokenAuthMixin

from .forms import EnvmodulesCommandRecordForm, EnvmodulesEventRecordForm


class BaseRecordView(TokenAuthMixin, View):

    record_form = None

    def post(self, request):
        form = self.record_form(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        form.save()
        return HttpResponse()


class EnvmodulesCommandRecordView(BaseRecordView):
    record_form = EnvmodulesCommandRecordForm


class EnvmodulesEventRecordView(BaseRecordView):
    record_form = EnvmodulesEventRecordForm
