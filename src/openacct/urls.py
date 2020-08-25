from django.urls    import path

from .views import UserListView, UserView, ProjectListView, ProjectView, SystemView

app_name = "openacct"

urlpatterns = [
    path('user_list/', UserListView.as_view(), name='user_list'),
    path('user/<int:byid>/', UserView.as_view(), name='user_byid'),
    path('user/<byname>/', UserView.as_view(), name='user_byname'),
    path('project_list/', ProjectListView.as_view(), name='project_list'),
    path('project/<int:byid>/', ProjectView.as_view(), name='project_byid'),
    path('project/<byname>/', ProjectView.as_view(), name='project_byname'),
    path('system/<int:byid>/', SystemView.as_view(), name='system_byid'),
    path('system/<byname>/', SystemView.as_view(), name='system_byname'),
]
