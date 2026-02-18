# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/18/2026
# Description: Class-based views for mini_insta (list all profiles and show one profile).

from django.views.generic import ListView, DetailView
from .models import Profile


class ProfileListView(ListView):
    """Display a page showing all Profile records."""
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"


class ProfileDetailView(DetailView):
    """Display a page showing a single Profile record."""
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

