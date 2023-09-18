from django.db import models


class LoginRecord(models.Model):
    when = models.DateTimeField()
    host = models.CharField(max_length=256)
    service = models.CharField(max_length=256)
    method = models.CharField(max_length=256, blank=True, null=True)
    user = models.CharField(max_length=32)
    fromhost = models.CharField(max_length=256)
    result = models.CharField(max_length=64, blank=True, default='success')
    reason = models.CharField(max_length=256, blank=True, null=True)
    locations = models.ManyToManyField("Location", through="LoginLocation")
    
    def __str__(self):
        return f"{self.user} - {self.when}"

class Location(models.Model):
    country = models.CharField(max_length=256)
    state = models.CharField(max_length=256)
    city = models.CharField(max_length=256)

class LoginLocation(models.Model):
    role = models.CharField(max_length=32)
    login = models.ForeignKey(LoginRecord, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
