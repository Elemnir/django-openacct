import re

from django.db import models


class User(models.Model):
    """A user account. Is a member of zero or more projects, and can
    have a default_project selected for setting a default when 
    submitting jobs.
    """
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32, unique=True)
    realname    = models.CharField(max_length=128, blank=True)
    active      = models.BooleanField(blank=True, default=True)
    projects    = models.ManyToManyField('Project', blank=True)
    default_project = models.ForeignKey('Project', on_delete=models.CASCADE, 
        blank=True, null=True, related_name='+'
    )

    def __str__(self):
        return 'User: {}'.format(self.name)


class Project(models.Model):
    """The root entity for ownership/membership. The pi (primary 
    investigator) is the project's owner and should usually add the
    project to their list of projects. Can be optionally associated
    with an LDAP group for file access purposes.
    """
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32, unique=True)
    ldap_group  = models.CharField(max_length=32, blank=True)
    active      = models.BooleanField(blank=True, default=True)
    pi          = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024, blank=True, default="")
        
    def __str__(self):
        return 'Project: {} - {}'.format(self.name, self.description)

    def get_index_value(self):
        m = re.search('\d+$', self.name)
        return int(m.group(0), 10) if m else 0

    @classmethod
    def next_index(cls, prefix):
        """Given a prefix string, find all projects matching the given 
        prefix and then return the next unused integer index for that
        prefix. Returns 1 if the prefix isn't found.
        """
        return 1 + max([
            p.get_index_value() for p in cls.objects.filter(name__icontains=prefix)
        ] + [0])


class UserProjectEvent(models.Model):
    """Records of changes to a project's membership or ownership."""
    EVENT_TYPES = (
        ('NEWPI', 'NEWPI'),
        ('ADDED', 'ADDED'),
        ('REMOVED', 'REMOVED'),
    )
    created     = models.DateTimeField(auto_now_add=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE)
    event_type  = models.CharField(max_length=16, choices=EVENT_TYPES)

    def __str__(self):
        return 'UPEvent: {} - {} - {}'.format(self.event_type, self.project.name, self.user.name)


class Account(models.Model):
    """Accounts provide the linkage between a project and the services to which 
    that project has access. Transactions are billed to one of a project's 
    accounts, allowing for multple concurrent billing streams to be easily 
    distinguished. Optionally an expiration date for an account can be 
    specified for accounting purposes.
    """
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32)
    active      = models.BooleanField(blank=True, default=True)
    expires     = models.DateTimeField(blank=True)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE)
    services    = models.ManyToManyField('Service', blank=True)

    def __str__(self):
        return 'Account: {}'.format(self.name)

    def get_index_value(self):
        m = re.search('\d+$', self.name)
        return int(m.group(0), 10) if m else 0

    @classmethod
    def next_index(cls, prefix):
        """Given a prefix string, find all accounts matching the given
        prefix and then return the next unused integer index for that
        prefix. Returns 1 if the prefix isn't found.
        """
        return 1 + max([
            a.get_index_value() for a in cls.objects.filter(name__icontains=prefix)
        ] + [0])


class System(models.Model):
    """The root entity under which services are grouped. Examples could be a 
    whole cluster, a discrete partition within a cluster, a storage system, or 
    more abstract concepts like a particular funding award."""
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32, unique=True)
    active      = models.BooleanField(blank=True, default=True)
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return 'System: {}'.format(self.name)


class Service(models.Model):
    """A service is any consumable resource provided by a system. Each service 
    can have its own units and charge rate, and can be anything from core hours
    for a particular cluster partition or space allocated on a storage system, 
    to hours of billed support or reserved resources for a priority or 
    preemptive access-based system.
    """
    created     = models.DateTimeField(auto_now_add=True)
    name        = models.CharField(max_length=32)
    units       = models.CharField(max_length=32)
    active      = models.BooleanField(blank=True, default=True)
    system      = models.ForeignKey(System, on_delete=models.CASCADE)
    charge_rate = models.FloatField(blank=True, default=0)
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return 'Service: {}'.format(self.name)


class Transaction(models.Model):
    """A transaction is a record of consumption of a service's resources by a 
    particular user, and then attributed to a single account for charging. Usage
    and charging are kept as separate entities to allow for discretionary 
    billing or selective application of discounts. In addition to CREDIT and 
    DEBIT transactions, AUDIT transactions allow a mechanism for monitoring a
    resource's usage in such a way that they are distinguishable from 
    transactions intended to be charged, as well as GRANT and REVOKE 
    transactions which provide sentinels for when an account is gained or lost
    privileges for utilizing a service.
    """
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

    def __str__(self):
        return 'Tx: {} - {} - {}'.format(self.created, self.service.name, self.account.name)


class Job(models.Model):
    """Jobs encapsulate common metadata provided by batch schedulers about 
    their workloads. Beyond the metadata, a job can create a number of
    transactions for capturing information about resources it used for
    accounting and billing purposes. The wallclock related fields contain
    integers intended to represent the relevant time duration in seconds. Many 
    other fields are left as character fields to capture the raw data from the 
    batch scheduler. Translation layers would then be responsible for linking 
    the raw information to the site-wide accounting.
    """
    created     = models.DateTimeField(auto_now_add=True)
    queued      = models.DateTimeField()
    started     = models.DateTimeField(blank=True, null=True)
    completed   = models.DateTimeField(blank=True, null=True)
    jobid       = models.CharField(max_length=32, unique=True)
    name        = models.CharField(max_length=64, blank=True, default='')
    submit_host = models.CharField(max_length=64, blank=True, default='')
    host_list   = models.CharField(max_length=1024, blank=True, default='')
    account     = models.CharField(max_length=64, blank=True, default='')
    qos         = models.CharField(max_length=64, blank=True, default='')
    job_script  = models.TextField(blank=True, default='')
    transactions   = models.ManyToManyField(Transaction, blank=True)
    wall_requested = models.IntegerField()
    wall_duration  = models.IntegerField(blank=True)

    def __str__(self):
        return 'Job: {} - {}'.format(self.jobid, self.name)


class StorageCommitment(models.Model):
    """Storage commitments encapsulate extended information regarding the 
    allocation of storage resources. Transactions can be attached to a 
    commitment to track and bill for storage usage. 
    """
    DIR_TYPES = (
        ('HOME', 'Home Directory'),
        ('PROJECT', 'Project Space'),
        ('SCRATCH', 'Scratch Space'),
        ('TEMP', 'Temporary Space'),
    )
    created         = models.DateTimeField(auto_now_add=True)
    dir_type        = models.CharField(max_length=16, choices=DIR_TYPES)
    project         = models.ForeignKey(Project, on_delete=models.CASCADE)
    filesystem      = models.CharField(max_length=64)
    path            = models.CharField(max_length=256)
    commitment      = models.BigIntegerField(default=0, blank=True, null=True)
    allocated       = models.DateTimeField(blank=True, null=True)
    end_date        = models.DateTimeField(blank=True, null=True)
    reclaimed       = models.DateTimeField(blank=True, null=True)
    uid             = models.IntegerField(blank=True, default=0)
    gid             = models.IntegerField(blank=True, default=0)
    pid             = models.IntegerField(blank=True, default=0)
    permissions     = models.CharField(max_length=8, default='0700')
    is_purged       = models.BooleanField(blank=True, default=True)
    transactions    = models.ManyToManyField(Transaction, blank=True)

    def __str__(self):
        return 'StorComm: {} - {}'.format(self.filesystem, self.path)

