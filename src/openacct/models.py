import re

from collections import defaultdict
from typing import Union

from django.db import models
from django.db.models.signals import m2m_changed

class User(models.Model):
    """A user account. Is a member of zero or more projects, and can
    have a default_project selected for setting a default when
    submitting jobs.
    """

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32, unique=True)
    realname = models.CharField(max_length=128, blank=True)
    active = models.BooleanField(blank=True, default=True)
    projects = models.ManyToManyField("Project", blank=True)
    default_project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, 
        blank=True, null=True, related_name="+"
    )

    def __str__(self):
        return "{}".format(self.name)


class Project(models.Model):
    """The root entity for ownership/membership. The pi (primary
    investigator) is the project's owner and should usually add the
    project to their list of projects. Can be optionally associated
    with an LDAP group for file access purposes.
    """

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32, unique=True)
    ldap_group = models.CharField(max_length=32, blank=True)
    active = models.BooleanField(blank=True, default=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, related_name="children",
        blank=True, null=True, default=None
    )
    pi = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_projects"
    )
    managers = models.ManyToManyField(
        User, blank=True, related_name="managed_projects"
    )
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return "{} - {}".format(self.name, self.description)

    def get_index_value(self):
        m = re.search(r"\d+$", self.name)
        return int(m.group(0), 10) if m else 0

    @classmethod
    def next_index(cls, prefix: str):
        """Given a prefix string, find all projects matching the given
        prefix and then return the next unused integer index for that
        prefix. Returns 1 if the prefix isn't found.
        """
        return 1 + max(
            [p.get_index_value() for p in cls.objects.filter(name__icontains=prefix)]
            + [0]
        )

    def can_edit(self, user: Union[User, str]):
        """Return whether or not the given User is allowed to edit the
        project. User can be either a User object or the name of a User
        which will first be looked up.
        """
        user = user if isinstance(user, User) else User.objects.get(name=user)
        if user == self.pi:
            return True
        return self.managers.filter(name=user.name).exists()


class UserProjectEvent(models.Model):
    """Records of changes to a project's membership or ownership."""

    EVENT_TYPES = (
        ("NEWPI", "New PI"),
        ("ADDMGR", "Add Manager"),
        ("REMOVEMGR", "Remove Manager"),
        ("ADDMEM", "Add Member"),
        ("REMOVEMEM", "Remove Member"),
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=16, choices=EVENT_TYPES)

    def __str__(self):
        return "{} - {} - {}".format(
            self.event_type, self.project.name, self.user.name
        )


def project_members_changed(sender, **kwargs):
    """This signal handler will automatically record changes to a
    project's list of members and managers. Will not detect if the m2m
    relations are cleared.
    """
    if kwargs["action"] == "post_add":
        etype = "ADD"
    elif kwargs["action"] == "post_remove":
        etype = "REMOVE"
    else:
        return

    if sender == Project.managers.through:
        etype += "MGR"
    elif sender == User.projects.through:
        etype += "MEM"

    for pk in kwargs["pk_set"]:
        if kwargs["model"] == Project:
            UserProjectEvent.objects.create(
                project_id=pk, user=kwargs["instance"], event_type=etype
            )
        elif kwargs["model"] == User:
            UserProjectEvent.objects.create(
                project=kwargs["instance"], user_id=pk, event_type=etype
            )


m2m_changed.connect(project_members_changed, sender=Project.managers.through)
m2m_changed.connect(project_members_changed, sender=User.projects.through)


class Account(models.Model):
    """Accounts provide the linkage between a project and the services to which
    that project has access. Transactions are billed to one of a project's
    accounts, allowing for multple concurrent billing streams to be easily
    distinguished. Optionally an expiration date for an account can be
    specified for accounting purposes.
    """

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    active = models.BooleanField(blank=True, default=True)
    expires = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    services = models.ManyToManyField("Service", blank=True)

    def __str__(self):
        return "{}".format(self.name)

    def get_index_value(self):
        """Returns the numeric integer component at the end of a project
        name, if it has one, otherwise returns 0.
        """
        m = re.search(r"\d+$", self.name)
        return int(m.group(0), 10) if m else 0

    @classmethod
    def next_index(cls, prefix):
        """Given a prefix string, find all accounts matching the given
        prefix and then return the next unused integer index for that
        prefix. Returns 1 if the prefix isn't found.
        """
        return 1 + max(
            [a.get_index_value() for a in cls.objects.filter(name__icontains=prefix)]
            + [0]
        )


class System(models.Model):
    """The root entity under which services are grouped. Examples could be a
    whole cluster, a discrete partition within a cluster, a storage system, or
    more abstract concepts like a particular funding award."""

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32, unique=True)
    active = models.BooleanField(blank=True, default=True)
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return "{}".format(self.name)


class Service(models.Model):
    """A service is any consumable resource provided by a system. Each service
    can have its own units and charge rate, and can be anything from core hours
    for a particular cluster partition or space allocated on a storage system,
    to hours of billed support or reserved resources for a priority or
    preemptive access-based system.
    """

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    units = models.CharField(max_length=32)
    active = models.BooleanField(blank=True, default=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    charge_rate = models.FloatField(blank=True, default=0)
    description = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return "{}".format(self.name)


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
        ("AUDIT", "AUDIT"),
        ("CREDIT", "CREDIT"),
        ("DEBIT", "DEBIT"),
        ("GRANT", "GRANT"),
        ("REVOKE", "REVOKE"),
    )
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(blank=True, default=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    amt_used = models.FloatField()
    amt_charged = models.FloatField(blank=True, default=0.0)
    tx_type = models.CharField(max_length=16, choices=TX_TYPES)

    def __str__(self):
        return "{} - {} - {}".format(
            self.created, self.service.name, self.account.name
        )


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

    created = models.DateTimeField(auto_now_add=True)
    queued = models.DateTimeField()
    started = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)
    jobid = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64, blank=True, default="")
    cluster = models.CharField(max_length=32, blank=True, default="")
    submitter = models.CharField(max_length=32, blank=True, default="")
    submit_host = models.CharField(max_length=64, blank=True, default="")
    host_list = models.CharField(max_length=1024, blank=True, default="")
    account = models.CharField(max_length=64, blank=True, default="")
    partition = models.CharField(max_length=64, blank=True, default="")
    qos = models.CharField(max_length=64, blank=True, default="")
    job_script = models.TextField(blank=True, default="")
    transactions = models.ManyToManyField(Transaction, blank=True)
    tres_requested = models.TextField(blank=True, default="")
    tres_allocated = models.TextField(blank=True, default="")
    wall_requested = models.IntegerField()
    wall_duration = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.jobid, self.name)


class StorageCommitment(models.Model):
    """Storage commitments encapsulate extended information regarding the
    allocation of storage resources. Transactions can be attached to a
    commitment to track and bill for storage usage.
    """

    DIR_TYPES = (
        ("HOME", "Home Directory"),
        ("PROJECT", "Project Space"),
        ("SCRATCH", "Scratch Space"),
        ("TEMP", "Temporary Space"),
    )
    created = models.DateTimeField(auto_now_add=True)
    dir_type = models.CharField(max_length=16, choices=DIR_TYPES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    filesystem = models.CharField(max_length=64)
    path = models.CharField(max_length=256)
    commitment = models.BigIntegerField(default=0, blank=True, null=True)
    allocated = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    reclaimed = models.DateTimeField(blank=True, null=True)
    uid = models.IntegerField(blank=True, default=0)
    gid = models.IntegerField(blank=True, default=0)
    pid = models.IntegerField(blank=True, default=0)
    permissions = models.CharField(max_length=8, default="0700")
    is_purged = models.BooleanField(blank=True, default=True)
    transactions = models.ManyToManyField(Transaction, blank=True)

    def __str__(self):
        return "{} - {}".format(self.filesystem, self.path)


class Invoice(models.Model):
    """A project usage invoice with related BalanceSheets."""
    created = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    predecessor = models.ForeignKey(
        "self", on_delete=models.SET_NULL, related_name="descendants",
        blank=True, null=True, default=None
    )

    def previous_account_balance(self, account):
        """Determine the previous balance for the give account from a
        predecessor Invoice, if one exists and contains a BalanceSheet 
        for that account, otherwise return 0.0
        """
        balance = 0.0
        if not self.predecessor:
            return balance
        try:
            previous = self.predecessor.sheets.get(account=account)
            balance = previous.balance
        except BalanceSheet.DoesNotExist:
            pass
        return balance

    def generate_balance_sheets(self):
        """Iterate active project accounts, generating BalanceSheets for
        each. The invoking Invoice must have been previously saved to
        the database, otherwise it will not have a valid primary key
        """
        for account in self.project.account_set.filter(active=True):
            balance = self.previous_account_balance(account)
            data = defaultdict(
                lambda : defaultdict(lambda : {"c": 0.0, "u": 0.0})
            )
            txs = Transaction.objects.filter(
                account=account,
                created__gte=self.start_time,
                created__lte=self.end_time
            ).select_related("user", "service")
            for tx in txs:
                amt_used, amt_charged = 0, 0
                if tx.type == "DEBIT":
                    amt_used, amt_charged = tx.amt_used, tx.amt_charged
                elif tx.type == "CREDIT":
                    amt_used, amt_charged = -tx.amt_used, -tx.amt_charged

                data[tx.user.name][tx.service.name]["u"] += amt_used
                data[tx.user.name][tx.service.name]["c"] += amt_charged
                balance += amt_charged

            BalanceSheet.objects.create(
                invoice=self,
                account=account,
                balance=balance,
                transactions=txs,
                contents=data
            )


class BalanceSheet(models.Model):
    """An itemized list of transactions which are processed to calculate usage
    and balance summaries. The ``contents`` field will be a JSON object
    aggregating the transactions into balances and usage by user and service.
    """
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="sheets"
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.FloatField(blank=True, default=0.0)
    transactions = models.ManyToManyField(Transaction, blank=True)
    contents = models.JSONField(blank=True, default=dict)
