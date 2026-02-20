# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/18/2026
# Description: Class-based views for mini_insta (list all profiles and show one profile).

from django.views.generic import ListView, DetailView
from .models import Profile, Post, Photo
from django.views.generic.edit import CreateView
from .forms import CreatePostForm


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

class PostDetailView(DetailView):
    """Display a page showing a single Post record."""
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"

class CreatePostView(CreateView):
    """Create a new Post for a specific Profile (and one Photo)."""
    model = Post
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        """Add the Profile (from the URL pk) to the template context."""
        context = super().get_context_data(**kwargs)
        context["profile"] = Profile.objects.get(pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        """
        Attach Profile FK to the Post before saving,
        then create one Photo using the submitted image_url.
        """
        profile = Profile.objects.get(pk=self.kwargs["pk"])
        form.instance.profile = profile

        response = super().form_valid(form) 

        image_url = form.cleaned_data.get("image_url")
        Photo.objects.create(post=self.object, image_url=image_url)

        return response

