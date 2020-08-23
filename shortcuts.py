from datetime import datetime

from .models import User, Project, Account, System, Service, Transaction, Job, StorageCommitment


def create_project(name, pi_name, description="", ldap_group="", create_account=True,
        account_name=None, account_duration=datetime.timedelta(days=365)):
    pi = User.objects.get(name=pi_name)
    project = Project.objects.create(name=name, pi=pi, description=description, ldap_group="")
    pi.projects.add(project)
    if create_account:
        create_account(project, name=account_name, duration=account_duration)
    return project


def create_account(project, name=None duration=datetime.timedelta(days=365):
    project = project if isinstance(project, Project) else Project.objects.get(name=project)
    name = name if name else '{0}-{1}'.format(project.name, Account.next_index(project.name+'-'))
    return Account.objects.create(
        name=name, project=project, expires=datetime.now()+account_duration
    )


def add_user_to_project(user, project):
    user = user if isinstance(user, User) else User.objects.get(name=user)
    project = project if isinstance(project, Project) else Project.objects.get(name=project)
    user.projects.add(project)


def grant_service_access(service, project=None, account=None):
    service = service if isinstance(service, Service) else service.objects.get(name=service)
    
    if account:
        account = account if isinstance(account, Account) else account.objects.get(name=account)
        Transaction.objects.create(
            service=service, account=account, tx_type='GRANT', 
            creator=account.project.pi, amt_used=0.0
        )
    elif project:
        project = project if isinstance(project, Project) else Project.objects.get(name=project)
        for acct in Account.objects.filter(project=project, active=True):
            Transaction.objects.create(
                service=service, account=acct, tx_type='GRANT', 
                creator=project.pi, amt_used=0.0
            )
    else:
        raise TypeError('Must provide either project or account')



