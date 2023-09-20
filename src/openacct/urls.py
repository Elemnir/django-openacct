from django.urls import path

from .views import (
    UserListView,
    UserView,
    ProjectListView,
    ProjectView,
    SystemListView,
    SystemView,
    ServiceView,
    JobEditView,
    JobListView,
    JobView,
)

app_name = "openacct"

urlpatterns = [
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("user_id/<int:byid>/", UserView.as_view(), name="user_byid"),
    path("user/<byname>/", UserView.as_view(), name="user_byname"),
    path("project_list/", ProjectListView.as_view(), name="project_list"),
    path("project_id/<int:byid>/", ProjectView.as_view(), name="project_byid"),
    path("project/<byname>/", ProjectView.as_view(), name="project_byname"),
    path("system_list/", SystemListView.as_view(), name="system_list"),
    path("system_id/<int:byid>/", SystemView.as_view(), name="system_byid"),
    path("system/<byname>/", SystemView.as_view(), name="system_byname"),
    path("service_id/<int:byid>/", ServiceView.as_view(), name="service_byid"),
    path("service/<byname>/", ServiceView.as_view(), name="service_byname"),
    path("job_list/", JobListView.as_view(), name="job_list"),
    path("job_id/<int:byid>/", JobView.as_view(), name="job_byid"),
    path("job/<byname>/", JobView.as_view(), name="job_byname"),
]
