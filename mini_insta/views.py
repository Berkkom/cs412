from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView
# Create your views here.
class ProfileListView(ListView):
    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'