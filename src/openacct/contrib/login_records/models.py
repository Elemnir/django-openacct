from django.db import models


class LoginRecord(models.Model):
    when = models.DateTimeField()
    host = models.CharField(max_length=64)
    service = models.CharField(max_length=32)
    method = models.CharField(max_length=32, blank=True, null=True)
    user = models.CharField(max_length=32)
    fromhost = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.user} - {self.when}"
