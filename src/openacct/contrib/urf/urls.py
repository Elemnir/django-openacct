from django.urls    import path

from .models import RequestPluginLoader
from .views import RequestDetailView

app_name = "urf"

urlpatterns = [
    path('view/<int:pk>/', RequestDetailView.as_view(), name='review'),
] + RequestPluginLoader().urls # Add the URLs for the plugins
