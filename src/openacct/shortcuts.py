"""
    openacct.shortcuts
    ~~~~~~~~~~~~~~~~~~

    This module provides a number of helper functions for performing 
    common operations on OpenAcct objects.
"""
from datetime import timedelta

from django.utils.timezone  import now

from .models    import (User, Project, UserProjectEvent, Account, System, Service, 
                        Transaction, Job, StorageCommitment)


def create_project(name, pi, description="", ldap_group="", do_create_account=True,
        account_name=None, account_duration=timedelta(days=365)):
    """Create and return a Project with the given traits. ``name`` should be the name 
    of project to create, and ``pi`` must either be an instance of User, or the string 
    name of a User in the database. 
    
    Optional ``description`` and ``ldap_group`` parameters set those respective 
    attributes on the created project.

    If ``do_create_account`` is True, an Account will be 
    created by calling ``create_account`` with ``account_name`` and ``account_duration`` 
    as its parameters, otherwise those parameters are ignored.
    """
    pi = pi if isinstance(pi, User) else User.objects.get(name=pi)
    project = Project.objects.create(name=name, pi=pi, description=description, ldap_group=ldap_group)
    add_user_to_project(pi, project)
    if do_create_account:
        create_account(project, name=account_name, duration=account_duration)
    return project


def create_account(project, name=None, duration=timedelta(days=365)):
    """Create and return an Account for the given Project. ``project`` must either 
    be an instance of Project, or the string name of a Project in the database. 

    If ``name`` is not provided, the Account will be named after the Project followed 
    by a dash and an index number. (For example, The first account for a project named 
    "test" will be named "test-1", the second will be "test-2", etc.)
    """
    project = project if isinstance(project, Project) else Project.objects.get(name=project)
    name = name if name else '{0}-{1}'.format(project.name, Account.next_index(project.name+'-'))
    return Account.objects.create(
        name=name, project=project, expires=now() + duration
    )


def add_user_to_project(user, project):
    """Add the given User to the given Project. Each argument can either be an instance of their
    respective objects, or the string name of a database object of their respective types.
    """
    user = user if isinstance(user, User) else User.objects.get(name=user)
    project = project if isinstance(project, Project) else Project.objects.get(name=project)
    UserProjectEvent.objects.create(user=user, project=project, event_type='ADDED')
    user.projects.add(project)


def remove_user_from_project(user, project):
    """Remove the given User from the given Project. Each argument can either be an instance of 
    their respective objects, or the string name of a database object of their respective types.
    """
    user = user if isinstance(user, User) else User.objects.get(name=user)
    project = project if isinstance(project, Project) else Project.objects.get(name=project)
    UserProjectEvent.objects.create(user=user, project=project, event_type='REMOVED')
    user.projects.remove(project)


def grant_service_access(service, account=None, project=None):
    """Grant access to a given Service to a single Account, or all active accounts on a Project.

    Must provide either the ``account`` or ``project`` argument. Each argument can either be an 
    instance of their respective objects, or the string name of a database object of their 
    respective types.
    """
    service = service if isinstance(service, Service) else Service.objects.get(name=service)
    if account:
        account = account if isinstance(account, Account) else Account.objects.get(name=account)
        account.services.add(service)
        Transaction.objects.create(
            service=service, account=account, tx_type='GRANT', 
            creator=account.project.pi, amt_used=0.0
        )
    elif project:
        project = project if isinstance(project, Project) else Project.objects.get(name=project)
        for acct in Account.objects.filter(project=project, active=True):
            acct.services.add(service)
            Transaction.objects.create(
                service=service, account=acct, tx_type='GRANT', 
                creator=project.pi, amt_used=0.0
            )
    else:
        raise TypeError('Must provide either project or account')


def revoke_service_access(service, account=None, project=None):
    """Revoke access to a given Service from a single Account, or all active accounts on a Project.

    Must provide either the ``account`` or ``project`` argument. Each argument can either be an 
    instance of their respective objects, or the string name of a database object of their 
    respective types.
    """
    service = service if isinstance(service, Service) else Service.objects.get(name=service)
    if account:
        account = account if isinstance(account, Account) else Account.objects.get(name=account)
        account.services.remove(service)
        Transaction.objects.create(
            service=service, account=account, tx_type='REVOKE', 
            creator=account.project.pi, amt_used=0.0
        )
    elif project:
        project = project if isinstance(project, Project) else Project.objects.get(name=project)
        for acct in Account.objects.filter(project=project, active=True):
            acct.services.remove(service)
            Transaction.objects.create(
                service=service, account=acct, tx_type='REVOKE', 
                creator=project.pi, amt_used=0.0
            )
    else:
        raise TypeError('Must provide either project or account')


def record_transaction(amt_used, service, user, account=None, project=None, 
        active=True, tx_type='DEBIT', amt_charged=0.0):
    """Create and return a transaction with the given parameters.

    Must provide either the ``account`` or ``project`` argument. ``service``, 
    ``user``, ``account`` and ``project`` can either be an instance of their 
    respective objects, or the string name of a database object of their 
    respective types.
    """
    service = service if isinstance(service, Service) else Service.objects.get(name=service)
    user = user if isinstance(user, User) else User.objects.get(name=user)
    if account:
        account = account if isinstance(account, Account) else Account.objects.get(name=account)
    elif project:
        account = Account.objects.filter(project=project, active=True).order_by('-created').first()
    else:
        raise TypeError('Must provide either project or account')
    
    return Transaction.objects.create(
        amt_used=amt_used, service=service, creator=user, account=account, active=active,
        tx_type=tx_type, amt_charged=amt_charged
    )


def record_job(jobid, queued, wall_requested, name='', submit_host='', host_list='', 
        qos='', job_script='', started=None, completed=None, wall_duration=None, 
        transactions=[]):
    """Create and return a job with the given parameters."""
    kwargs = {
        'jobid': jobid, 'queued': queued, 'wall_requested': wall_requested, 
        'name': name, 'submit_host': submit_host, 'host_list': host_list, 
        'qos': qos, 'job_script': job_script
    }
    if started: kwargs['started'] = started
    if completed: kwargs['completed'] = completed
    if wall_duration: kwargs['wall_duration'] = wall_duration

    job = Job.objects.create(**kwargs)
    if transactions:
        job.transactions.add(transactions)
    return job

