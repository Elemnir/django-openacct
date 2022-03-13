from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.module_loading import import_string
from django.views.generic import View

from .apps import UrfConfig
from .models import (
    EmailTemplate, 
    Request, 
    RequestLogEntry, 
    RequestType, 
    RequestPluginLoader,
    request_log,
)


CHECK_ADMIN_VALUE = getattr(settings, 'USER_REQUESTS_CHECK_ADMIN', lambda u: u.is_staff)
check_admin = (
    CHECK_ADMIN_VALUE if callable(CHECK_ADMIN_VALUE) else import_string(CHECK_ADMIN_VALUE)
)


class RequestDetailView(LoginRequiredMixin, View):
    """Allows review of requests by admins as well as the user who
    submitted the request. The submitting user may confirm their
    request, publishing it to the list so admins can review it, or
    cancel it, deleting the request components. Admins may Approve,
    Deny, or mark the request as approved Pending review. They may also
    make minor alterations to fix typos. Interactions with the request
    after it is confirmed will be recorded and reported.
    """
    def get(self, request, pk):
        plugin_loader = RequestPluginLoader()
        req = get_object_or_404(Request, pk=pk)
        is_admin = check_admin(request.user)

        # Only an admin or the requester should be able to review a Request
        if req.requester != request.user.username and not is_admin:
            return HttpResponseForbidden()

        if is_admin:
            request_log(req, 'VIEW - {0}'.format(request.user))

        widgets = []
        for model in plugin_loader.request_types:
            widgets.extend(model.objects.filter(request=req))
        
        request.current_app = 'urf'
        return render(request, 'request_detail.html', {
            **admin.site.each_context(request),
            'req'           : req,
            'widgets'       : widgets,
            'title'         : "Request {}".format(req.pk),
            'history'       : RequestLogEntry.objects.filter(request=req),
            'email_options' : EmailTemplate.objects.all(),
            'is_admin'      : is_admin,
            'is_requester'  : req.requester == request.user.username,
            'opts'          : req._meta,
            'original'      : req,
            'has_view_permission': True,
        })

    def post(self, request, pk):
        req = get_object_or_404(Request, pk=pk)
        is_admin = check_admin(request.user)
        next = request.POST.get('next', req.review_url())
        
        actions = [ key.split("_")[1] for key in request.POST.keys() if "action_" in key ]
        action = actions[0] if actions else ''
        request_log(req, '{0} - {1}'.format(action, request.user))
        
        if req.requester != request.user.username and not is_admin:
            return HttpResponseForbidden() # Only an admin or the requester should view
        if not is_admin and action not in ('CONFIRM', 'CANCEL'):
            return HttpResponseForbidden() # The requester can only confirm or cancel
        
        if action == 'CONFIRM':
            req.on_confirmed()
        elif action == 'CANCELLED':
            req.status = action
            req.save()
        elif action == 'UPDATE':
            req.requester = request.POST.get('requester', req.requester)
            req.description = request.POST.get('description', req.description)
            req.notification_id = int(request.POST.get('notification', req.notification))
            req.save()
        elif action == 'PENDING':
            req.on_pending()
        elif action == 'APPROVED':
            req.on_approved()
        elif action == 'DECLINED':
            req.on_declined()
        elif action == 'PROCESSED':
            req.on_processed()
        
        return redirect(next)
