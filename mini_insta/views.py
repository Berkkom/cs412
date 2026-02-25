# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/24/2026
# Description: Class-based views for mini_insta, including profile/post display,
# creating/updating/deleting posts, updating profiles, follower/following pages,
# post feed, and search.

from django.views.generic import ListView, DetailView
from .models import Profile, Post, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import CreatePostForm, UpdateProfileForm
from django.urls import reverse
from django.shortcuts import render
from django.db.models import Q

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
        """Attach the Profile FK, save the Post, then create Photos from uploaded files."""
        profile = Profile.objects.get(pk=self.kwargs["pk"])
        form.instance.profile = profile

        response = super().form_valid(form)  # saves Post as self.object

        files = self.request.FILES.getlist("files")
        for f in files:
            Photo.objects.create(post=self.object, image_file=f)

        return response

class UpdateProfileView(UpdateView):
    """Update an existing Profile record."""
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"

class DeletePostView(DeleteView):
    """Delete an existing Post after confirmation."""
    model = Post
    template_name = "mini_insta/delete_post_form.html"

    def get_context_data(self, **kwargs):
        """Provide post and profile in the context for the delete template."""
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        context["profile"] = self.object.profile
        return context

    def get_success_url(self):
        """After deleting a post, return to the creator's profile page."""
        return reverse("show_profile", kwargs={"pk": self.object.profile.pk})


class UpdatePostView(UpdateView):
    """Update the caption of an existing Post."""
    model = Post
    fields = ["caption"]  
    template_name = "mini_insta/update_post_form.html"

class ShowFollowersDetailView(DetailView):
    """Show the followers list for a single Profile."""
    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = "profile"


class ShowFollowingDetailView(DetailView):
    """Show the following list for a single Profile."""
    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"

class PostFeedListView(ListView):
    """Display a feed of posts for the profiles followed by a given Profile."""
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        """Return the feed posts for the profile specified by pk in the URL."""
        self.profile = Profile.objects.get(pk=self.kwargs["pk"])
        return self.profile.get_post_feed()

    def get_context_data(self, **kwargs):
        """Add the profile to context for navigation (back to profile page)."""
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object.profile
        return context

class SearchView(ListView):
    """
    Search posts (caption) and profiles (username/display_name/bio_text)
    on behalf of a given Profile (pk from URL).
    """
    template_name = "mini_insta/search_results.html"
    context_object_name = "posts"

    def dispatch(self, request, *args, **kwargs):
        if "query" not in request.GET:
            profile = Profile.objects.get(pk=self.kwargs["pk"])
            return render(request, "mini_insta/search.html", {"profile": profile})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return the QuerySet of Posts whose caption contains the query."""
        q = self.request.GET.get("query", "").strip()
        if not q:
            return Post.objects.none()
        return Post.objects.filter(caption__icontains=q).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        """Add profile, query, matching posts, and matching profiles to context."""
        context = super().get_context_data(**kwargs)

        profile = Profile.objects.get(pk=self.kwargs["pk"])
        q = self.request.GET.get("query", "").strip()

        matching_posts = self.get_queryset()

        if q:
            matching_profiles = Profile.objects.filter(
                Q(username__icontains=q) |
                Q(display_name__icontains=q) |
                Q(bio_text__icontains=q)
            )
        else:
            matching_profiles = Profile.objects.none()

        context["profile"] = profile
        context["query"] = q
        context["posts"] = matching_posts
        context["profiles"] = matching_profiles
        return context
