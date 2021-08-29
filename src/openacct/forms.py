from django.forms   import ModelForm

from .models    import (User, Project, UserProjectEvent, Account, System, Service, 
                        Transaction, Job, StorageCommitment)
from .shortcuts import add_user_to_project, create_account


class UpdateOnlyModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or not isinstance(kwargs['instance'], self._meta.model):
            raise ValueError("This form can only be used on an existing instance")
        super().__init__(*args, **kwargs)


class JobQueuedForm(ModelForm):
    class Meta:
        meta = Job
        fields = [
            'queued', 'jobid', 'name', 'submit_host', 'account', 'qos', 
            'job_script', 'wall_requested'
        ]


class JobStartedForm(UpdateOnlyModelForm):
     class Meta:
        meta = Job
        fields = ['started', 'host_list']

   
class JobCompletedForm(UpdateOnlyModelForm):
     class Meta:
        meta = Job
        fields = ['started', 'completed', 'host_list', 'wall_duration']


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['pi', 'name', 'description', 'ldap_group']

    def save(self, commit=True):
        proj = super().save(commit)
        if commit:
            add_user_to_project(proj.pi, proj)
            create_account(proj)
        return proj

