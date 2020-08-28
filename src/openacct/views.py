from django.core                import serializers
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http                import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts           import render, get_object_or_404
from django.views.generic       import View 

from .models    import User, Project, Account, System, Service


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
        for field in ['name__icontains', 'realname__icontains']:
            if field in self.request and self.request.GET.get(field,''):
                filters[field] = self.request.GET[field]
        
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
            } for p in user.projects.all() if p.active ]
        }})


class ProjectListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Returns a list of projects. Supports GET parameter filters"""
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        filters = {'active': True} if 'active' in self.request.GET else {}
        for field in ['name__icontains', 'description__icontains']:
            if field in self.request and self.request.GET.get(field,''):
                filters[field] = self.request.GET[field]
        
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
            } for a in Account.objects.filter(project=project) if a.active ],
        }})
        

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
            } for s in Service.objects.filter(system=system) if s.active ],
        }})


#######################################################################
#
#   
#
#######################################################################
