from datetime   import datetime

from django.core                import serializers
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http                import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts           import render, get_object_or_404
from django.views.generic       import View 

from .models    import User, Project, Account, System, Service, Transaction, Job


#######################################################################
#
#   Informational Views
#
#######################################################################

class UserListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Returns a list of users, supports GET parameter filters"""
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        filters = {'active': True} if 'active' in self.request.GET else {}
        for field in ['name', 'realname']:
            if self.request.GET.get(field, False):
                filters[field + '__icontains'] = self.request.GET[field]
        
        payload = {'users':[]}
        for user in User.objects.filter(**filters).order_by('name'):
            payload['users'].append({
                'id': user.pk,
                'name': user.name, 
                'realname': user.realname,
                'created':  user.created,
            })
        return JsonResponse(payload)


class UserView(LoginRequiredMixin, View):
    """Returns a specific user"""
    def get(self, request, byid=None, byname=None):
        if (byid == None and byname == None) or (byid != None and byname != None):
            return HttpResponseBadRequest()
        
        user = (get_object_or_404(User, pk=byid) if byid 
            else get_object_or_404(User, name=byname))
        
        if not self.request.user.is_staff and self.request.username != user.name:
            return HttpResponseForbidden()
        
        return JsonResponse({'user': {
            'id': user.pk,
            'name': user.name, 
            'realname': user.realname,
            'created':  user.created,
            'projects': [ {
                'id': p.pk, 'name': p.name, 
                'ldap_group': p.ldap_group, 
                'description': p.description
            } for p in user.projects.filter(active=True)]
        }})


class ProjectListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Returns a list of projects. Supports GET parameter filters"""
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        filters = {'active': True} if 'active' in self.request.GET else {}
        for field in ['name', 'description']:
            if self.request.GET.get(field, False):
                filters[field + '__icontains'] = self.request.GET[field]
        
        payload = {'projects': []}
        for project in Project.objects.filter(**filters).order_by('name'):
            payload['projects'].append({
                'id': project.pk,
                'name': project.name,
                'pi': project.pi.name,
                'ldap_group': project.ldap_group,
                'description': project.description,
                'created': project.created,
            })
        return JsonResponse(payload)


class ProjectView(LoginRequiredMixin, View):
    """Returns a specific project"""
    def get(self, request, byid=None, byname=None):
        if (byid == None and byname == None) or (byid != None and byname != None):
            return HttpResponseBadRequest()
        
        project = (get_object_or_404(Project, pk=byid) if byid 
            else get_object_or_404(Project, name=byname))
        
        if (not self.request.user.is_staff and self.request.user.username 
                not in [u.name for u in project.user_set]):
            return HttpResponseForbidden()

        return JsonResponse({'project': {
            'id': project.pk,
            'name': project.name,
            'pi': project.pi.name,
            'ldap_group': project.ldap_group,
            'description': project.description,
            'created': project.created,
            'users': [ {
                'id': u.pk, 'name': u.name,
                'realname': u.realname,
                'created': u.created
            } for u in project.user_set.all() if u.active ],
            'accounts': [ {
                'id': a.pk, 'name': a.name, 
                'created': a.created,
                'expires': a.expires,
            } for a in Account.objects.filter(project=project, active=True)],
        }})
        

class SystemListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Returns a list of systems. Supports GET parameter filters"""
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        filters = {'active': True} if 'active' in self.request.GET else {}
        for field in ['name', 'description']:
            if self.request.GET.get(field, False):
                filters[field + '__icontains'] = self.request.GET[field]
        
        payload = {'systems': []}
        for system in System.objects.filter(**filters).order_by('name'):
            payload['systems'].append({
                'id': system.pk,
                'name': system.name,
                'description': system.description,
                'created': system.created,
            })
        return JsonResponse(payload)


class SystemView(LoginRequiredMixin, View):
    """Returns a specific system and services"""
    def get(self, request, byid=None, byname=None):
        if (byid == None and byname == None) or (byid != None and byname != None):
            return HttpResponseBadRequest()
        
        system = (get_object_or_404(System, pk=byid) if byid 
            else get_object_or_404(System, name=byname))

        return JsonResponse({'system': {
            'id': system.pk,
            'name': system.name,
            'description': system.description,
            'created': system.created,
            'services': [ {
                'id': s.pk, 'name': s.name, 'units': s.units,
                'charge_rate': s.charge_rate,
                'description': s.description,
            } for s in Service.objects.filter(system=system, active=True)],
        }})


class ServiceView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Returns a specific service and accounts allowed to use it"""
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, byid=None, byname=None):
        if (byid == None and byname == None) or (byid != None and byname != None):
            return HttpResponseBadRequest()
        
        service = (get_object_or_404(Service, pk=byid) if byid 
            else get_object_or_404(Service, name=byname))

        return JsonResponse({'service': {
            'id': service.pk,
            'name': service.name,
            'description': service.description,
            'system': service.system.name,
            'units': service.units,
            'charge_rate': service.charge_rate,
            'created': service.created,
            'accounts': [ {
                'id': a.pk, 'name': a.name,
                'project': a.project.name,
                'created': a.created,
                'expires': a.expires,
            } for a in Service.account_set.filter(active=True)],
        }})


class JobListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Returns a list of jobs. Supports GET parameter filters"""
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        filters = {}
        for field in ['name','jobid','submit_host','host_list','qos','job_script']:
            if self.request.GET.get(field, False):
                filters[field + '__icontains'] = self.request.GET[field]
        
        for field in ['queued_after', 'started_after', 'completed_after']:
            if self.request.GET.get(field, False):
                filters[field.replace('_after', '__gte')] = datetime.fromisoformat(
                    self.request.GET[field])
        
        for field in ['queued_before', 'started_before', 'completed_before']:
            if self.request.GET.get(field, False):
                filters[field.replace('_before', '__lte')] = datetime.fromisoformat(
                    self.request.GET[field])
        
        jobs = Job.objects.filter(**filters).order_by('jobid')
        
        # These filters are EXPENSIVE
        txfilters = {}
        for field in ['account', 'service', 'creator']:
            if self.request.GET.get(field, False):
                txfilters[field+'__name__icontains'] = self.request.GET[field]

        if txfilters:
            txfilters['active'] = True
            txids = Transaction.objects.filter(**txfilters).values_list('id', flat=True)
            jobs.filter(transactions__in=txids)
                
        payload = {'jobs': []}
        for job in jobs:
            payload['jobs'].append({
                'id': job.pk, 'jobid': job.jobid, 'name': job.name, 'qos': job.qos,
                'submit_host': job.submit_host, 'host_list': job.host_list,
                'queued': job.queued, 
                'started': job.started, 
                'completed': job.completed, 
                'wall_requested': job.wall_requested,
                'wall_duration': job.wall_duration, 
                'transactions': ( [ {
                    'id': t.pk, 'tx_type': t.tx_type, 'created': t.created, 
                    'amt_used': t.amt_used, 'amt_charged': t.amt_charged,
                    'service': t.service.name,
                    'account': t.account.name,
                    'creator': t.creator.name,
                } for t in job.transactions.filter(active=True).order_by('-created')] 
                if self.request.GET.get('show_txs', False) else [] )
            })
        return JsonResponse(payload)


class JobView(LoginRequiredMixin, View):
    """Returns a specific job"""
    def get(self, request, byid=None, byname=None):
        if (byid == None and byname == None) or (byid != None and byname != None):
            return HttpResponseBadRequest()
        
        job = (get_object_or_404(Job, pk=byid) if byid 
            else get_object_or_404(Job, name=byname))
        
        if (not self.request.user.is_staff and self.request.user.username 
                not in [t.creator.name for t in job.transactions]):
            return HttpResponseForbidden()

        return JsonResponse({'job' : {
            'id': job.pk, 'jobid': job.jobid, 'name': job.name, 'qos': job.qos,
            'submit_host': job.submit_host, 'host_list': job.host_list,
            'queued': job.queued, 'started': job.started, 'completed': job.completed, 
            'wall_requested': job.wall_requested, 'wall_duration': job.wall_duration, 
            'job_script': job.job_script,
            'transactions': [ {
                'id': t.pk, 'tx_type': t.tx_type, 'created': t.created, 
                'amt_used': t.amt_used, 'amt_charged': t.amt_charged,
                'service': t.service.name,
                'account': t.account.name,
                'creator': t.creator.name,
            } for t in job.transactions.filter(active=True).order_by('-created')]
        }})
        

#######################################################################
#
#   Create/Modify Views
#
#######################################################################

class JobChangeView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def put(self, request):
        pass
