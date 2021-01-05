import re

from django.db import models


class User(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32, unique=True)
    realname    = models.CharField(max_length=128, blank=True)
    active      = models.BooleanField(blank=True, default=True)
    projects    = models.ManyToManyField('Project', blank=True)
    default_project = models.ForeignKey('Project', on_delete=models.CASCADE, 
        blank=True, null=True, related_name='+'
    )

    def __str__(self):
        return '<User: {}>'.format(self.name)


class Project(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32, unique=True)
    ldap_group  = models.CharField(max_length=32, blank=True)
    active      = models.BooleanField(blank=True, default=True)
    pi          = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024, blank=True, default="")
        
    def __str__(self):
        return '{} - {}'.format(self.name, self.description)

    def get_index_value(self):
        m = re.search('\d+$', self.name)
        return int(m.group(0), 10) if m else 0

    @classmethod
    def next_index(cls, prefix):
        return 1 + max([
            p.get_index_value() for p in cls.objects.filter(name__icontains=prefix)
        ] + [0])


class UserProjectEvent(models.Model):
    EVENT_TYPES = (
        ('ADDED', 'ADDED'),
        ('REMOVED', 'REMOVED'),
    )
    created     = models.DateTimeField(auto_now_add=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE)
    event_type  = models.CharField(max_length=16, choices=EVENT_TYPES)


class Account(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32)
    active      = models.BooleanField(blank=True, default=True)
    expires     = models.DateTimeField(blank=True)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE)
    services    = models.ManyToManyField('Service', blank=True)

    def __str__(self):
        return '<Account: {}>'.format(self.name)

    def get_index_value(self):
        m = re.search('\d+$', self.name)
        return int(m.group(0), 10) if m else 0

    @classmethod
    def next_index(cls, prefix):
        return 1 + max([
            a.get_index_value() for a in cls.objects.filter(name__icontains=prefix)
        ] + [0])


class System(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32, unique=True)
    active      = models.BooleanField(blank=True, default=True)
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return '<System: {}>'.format(self.name)


class Service(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32)
    units       = models.CharField(max_length=32)
    active      = models.BooleanField(blank=True, default=True)
    system      = models.ForeignKey(System, on_delete=models.CASCADE)
    charge_rate = models.FloatField(blank=True, default=0)
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return '<Service: {}>'.format(self.name)


class Transaction(models.Model):
    TX_TYPES = (
        ('AUDIT', 'AUDIT'),
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT'),
        ('GRANT', 'GRANT'),
        ('REVOKE', 'REVOKE'),
    )
    created     = models.DateTimeField(auto_now_add=True)
    active      = models.BooleanField(blank=True, default=True)
    service     = models.ForeignKey(Service, on_delete=models.CASCADE)
    account     = models.ForeignKey(Account, on_delete=models.CASCADE)
    creator     = models.ForeignKey(User, on_delete=models.CASCADE)
    amt_used    = models.FloatField()
    amt_charged = models.FloatField(blank=True, default=0.0)
    tx_type     = models.CharField(max_length=16, choices=TX_TYPES)


class Job(models.Model):
    queued      = models.DateTimeField()
    started     = models.DateTimeField(blank=True, null=True)
    completed   = models.DateTimeField(blank=True, null=True)
    jobid       = models.CharField(max_length=32, unique=True)
    name        = models.CharField(max_length=64, blank=True, default='')
    submit_host = models.CharField(max_length=64, blank=True, default='')
    host_list   = models.CharField(max_length=1024, blank=True, default='')
    qos         = models.CharField(max_length=64, blank=True, default='')
    job_script  = models.TextField(blank=True, default='')
    transactions   = models.ManyToManyField(Transaction, blank=True)
    wall_requested = models.IntegerField()
    wall_duration  = models.IntegerField(blank=True)

    def __str__(self):
        return '<Job: {} - {}>'.format(self.jobid, self.name)


class StorageCommitment(models.Model):
    DIR_TYPES = (
        ('HOME', 'Home Directory'),
        ('PROJECT', 'Project Space'),
        ('SCRATCH', 'Scratch Space'),
        ('TEMP', 'Temporary Space'),
    )
    dir_type        = models.CharField(max_length=16, choices=DIR_TYPES)
    project         = models.ForeignKey(Project, on_delete=models.CASCADE)
    filesystem      = models.CharField(max_length=64)
    path            = models.CharField(max_length=256)
    commitment      = models.BigIntegerField(default=0, blank=True, null=True)
    registered      = models.DateTimeField(auto_now_add=True)
    created         = models.DateTimeField(blank=True, null=True)
    end_date        = models.DateTimeField(blank=True, null=True)
    reclaimed       = models.DateTimeField(blank=True, null=True)
    uid             = models.IntegerField(blank=True, default=0)
    gid             = models.IntegerField(blank=True, default=0)
    pid             = models.IntegerField(blank=True, default=0)
    permissions     = models.CharField(max_length=8, default='0700')
    is_purged       = models.BooleanField(blank=True, default=True)
    transactions    = models.ManyToManyField(Transaction, blank=True)
