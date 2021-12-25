import random

from django.db import models


def generate_token():
    """Returns a random 64-character alphanumeric string for use as tokens."""
    return "".join(
        [random.choice("abcdefghijfklmnopqrstuvwxyz0123456789") for i in range(64)]
    )


class AuthToken(models.Model):
    """Database model for storing and representing generic authentication
    tokens. Used by the ``AuthTokenMixin`` to secure a view class.
    """

    created = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=32)
    token = models.CharField(max_length=128, unique=True, default=generate_token)

    def __str__(self):
        return "{} - {}".format(self.name, self.created)
