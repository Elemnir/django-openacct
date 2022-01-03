from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from openacct.contrib.token_auth.mixins import TokenAuthMixin

from .forms import LoginRecordForm


class LoginRecordView(TokenAuthMixin, View):
    def post(self, request):
        form = LoginRecordForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        form.save()
        return HttpResponse()
