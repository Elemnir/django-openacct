from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.detail import DetailView

from openacct.models import User, Project


class UserDetailView(LoginRequiredMixin, DetailView):
    pass


class ProjectDetailView(LoginRequiredMixin, DetailView):
    pass
        
