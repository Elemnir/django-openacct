from django.db import models


class EnvmodulesCommandRecord(models.Model):
    when = models.DateTimeField(db_index=True)
    host = models.CharField(max_length=64)
    user = models.CharField(max_length=32)
    uuid = models.CharField(max_length=128, db_index=True)
    command = models.CharField(max_length=1024)

    # Additional information if in the context of a running job
    jobid = models.CharField(max_length=32, blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)
    cluster = models.CharField(max_length=32, blank=True, null=True)
 
    def __str__(self):
        return f"{self.user} - {self.command}"

    class Meta:
        db_table = "envmodules_command_record"


class EnvmodulesEventRecord(models.Model):
    caused = models.ForeignKey(EnvmodulesCommandRecord, on_delete=models.CASCADE)
    mode = models.CharField(max_length=2, choices=(("l","Load"),("u","Unload")))
    auto = models.BooleanField(blank=True, default=False)
    module = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.mode} - {self.module}"

    class Meta:
        db_table = "envmodules_event_record"
