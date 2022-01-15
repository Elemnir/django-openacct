import importlib

from django.conf                    import settings
from django.contrib.auth.models     import User
from django.core.mail               import send_mail
from django.db                      import models
from django.template                import Template, Context
from django.urls                    import reverse
from django.utils.html              import mark_safe
from django.utils.module_loading    import import_string


GET_EMAIL_VALUE = getattr(settings, 'USER_REQUESTS_GET_EMAIL',
    lambda u: User.objects.get(username=u).email
)
get_email = (
    GET_EMAIL_VALUE if callable(GET_EMAIL_VALUE) else import_string(GET_EMAIL_VALUE)
)

status_options = (
    ('NEW', 'NEW'),
    ('PENDING', 'PENDING'),
    ('APPROVED', 'APPROVED'),
    ('DECLINED', 'DECLINED'),
    ('PROCESSING', 'PROCESSING'),
    ('PROCESSED', 'PROCESSED'),
    ('FAILED', 'FAILED'),
    ('CANCELLED', 'CANCELLED'),
)


class EmailTemplate(models.Model):
    created         = models.DateTimeField(auto_now_add=True)
    name            = models.CharField(max_length=64)
    default_from    = models.CharField(max_length=64)
    subject         = models.CharField(max_length=64)
    body            = models.TextField()

    def send(self, to, from_email=None, context={}):
        send_mail(
            Template(self.subject).render(Context(context)),
            Template(self.body).render(Context(context)),
            from_email if from_email else self.default_from,
            to,
        )


class Request(models.Model):
    """Common information for all requests, facilitates ListView."""
    submitted       = models.DateTimeField(auto_now_add=True)
    requester       = models.CharField(max_length=32) # request.user.username
    confirmed       = models.BooleanField(blank=True, default=False)
    autoprocess     = models.BooleanField(blank=True, default=True)
    autonotify      = models.BooleanField(blank=True, default=True)
    notification    = models.ForeignKey(
        EmailTemplate, models.SET_DEFAULT, blank=True, null=True, default=1
    )
    description     = models.CharField(max_length=512, blank=True, default="")
    status          = models.CharField(
        max_length=16, choices=status_options, blank=True, default="NEW"
    )

    @classmethod
    def make_from_http_request(cls, request, status='NEW', description=''):
        """Create and save a new request object from an HTTP request."""
        req = cls(requester=request.user.username, status=status, description=description)
        req.save()
        return req

    def review_url(self):
        """Returns the request's review page URL"""
        return reverse('user_requests:review', kwargs={'pk': self.pk})

    def review_link(self):
        """Returns the request's review page as a link"""
        return mark_safe("<a href=\"{}\">View</a>".format(self.review_url()))

    def get_absolute_url(self):
        return self.review_url()
    
    def components(self):
        """Returns the components attached to this request"""
        plugin_loader = RequestPluginLoader()
        rval = []
        for rt in plugin_loader.request_types:
            rval.extend(rt.objects.filter(request=self))
        return rval

    def on_confirmed(self):
        for comp in self.components():
            comp.on_confirmed()
        self.confirmed = True
        self.save()

    def on_pending(self):
        for comp in self.components():
            comp.on_pending()
        self.status = 'PENDING'
        self.save()

    def on_approved(self):
        for comp in self.components():
            comp.on_approved()

        if self.autoprocess:
            self.on_processed()
        else:
            self.status = 'APPROVED'
            self.save()

    def on_declined(self):
        for comp in self.components():
            comp.on_declined()
        self.status = 'DECLINED'
        self.save()

    def on_processed(self):
        for comp in self.components():
            comp.on_processed()

        if self.autonotify:
            self.notification.send(
                [get_email(self.requester)], 
                context={'request':self, 'components':self.components()}
            )

        self.status = 'PROCESSED'
        self.save()


class RequestType(models.Model):
    """Abstract Base Class for all Requests"""
    request_visible = True
    request_description = "Set model's request_description to change this text"
    form_view_name = "user_requests:<name>"
    update_view_name = "user_requests:update_<name>"
    widget_template_path = "should_not_exist.html"

    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    @classmethod
    def approved_requests(cls):
        """Get all objects whose request is marked confirmed and approved."""
        return cls.objects.filter(request__status='APPROVED', request__confirmed=True)

    def get_absolute_url(self):
        """Used by the update view to get back to the review page."""
        return self.request.review_url()

    def on_confirmed(self):
        """Abstract method to be defined for a subclass which will be
        called after confirming a request containing this request type.
        """
        pass

    def on_approved(self):
        """Abstract method to be defined for each subclass which will be
        called for each approved request of that type. It is an error to
        not define this method.
        """
        raise NotImplementedError(
            "Subclasses of RequestType must define this method"
        )

    def on_declined(self):
        """Abstract method to be defined for a subclass which will be called
        after a request containing this request type is set to declined.
        """
        pass

    def on_pending(self):
        """Abstract method to be defined for a subclass which will be called
        after a request containing this request type is set to pending.
        """
        pass

    def on_processed(self):
        """Abstract method to be defined for a subclass which will be called
        after a request containing this request type is set to processed.
        """
        pass

    class Meta:
        abstract = True


class RequestLogEntry(models.Model):
    """Record actions taken by admins on the request."""
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    logged  = models.DateTimeField(auto_now_add=True)
    text    = models.CharField(max_length=128)

    def __str__(self):
        return '{0} - {1}'.format(self.logged, self.text)


def request_log(request, message):
    RequestLogEntry(request=request, text=message).save()


class RequestPluginLoader():
    def __init__(self):
        self.plugins = list([ 
            importlib.import_module(n) for n in settings.USER_REQUESTS_PLUGINS 
        ])
        self.request_types, self.urls = [], []

        for p in self.plugins:
            self.urls.extend(getattr(p, 'urlpatterns', []))
            self.request_types.extend(getattr(p, 'request_types', []))
