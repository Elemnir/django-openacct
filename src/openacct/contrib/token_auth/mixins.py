import re

from django.contrib.auth.mixins import AccessMixin
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from .models import AuthToken


@method_decorator(csrf_exempt, name="dispatch")
class TokenAuthMixin(AccessMixin):
    """When added to a view class, this mixin causes a request to first be
    authenticated by searching for an authentication token either through
    an Authorization header of the form ``Authorization: Token <token>``, or
    failing that as a ``token`` key in either the GET or POST data of the
    request.

    Make sure this mixin appears before any View classes in the subclass's
    inheritance list to ensure MRO chaining works appropriately for the
    ``dispatch`` method.
    """

    _TOKEN_KEY = "token"
    raise_exception = True

    def extract_token(self, request):
        """Searches for and returns the token from a request. Returns None if
        the token can't be found.
        """
        if "Authorization" in request.headers:
            m = re.match(r"Token (\w+)", request.headers.get("Authorization"))
            if m:
                return m.group(1)
        if self._TOKEN_KEY in request.GET:
            return request.GET.get(self._TOKEN_KEY)
        if self._TOKEN_KEY in request.POST:
            return request.POST.get(self._TOKEN_KEY)
        return None

    def validate_token(self, token):
        """Attempts to validate a token by searching for an instance matching
        it which hasn't yet expired. If such a token is located, it will
        automatically update the ``last_used`` field of the token. Returns True
        if the token is found, and False otherwise.
        """
        try:
            nt = now()
            token = AuthToken.objects.get(token=token, expires__gt=nt)
            token.last_used = nt
            token.save()
            return True
        except models.ObjectDoesNotExist:
            return False

    def dispatch(self, request, *args, **kwargs):
        """Overloads the default ``dispatch`` method of a View to first
        validate a token before continuing.
        """
        if not self.validate_token(self.extract_token(request)):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
