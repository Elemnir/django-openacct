from django.forms   import ModelForm

from .models    import (User, Project, UserProjectEvent, Account, System, Service, 
                        Transaction, Job, StorageCommitment)
from .shortcuts import add_user_to_project, create_account

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
