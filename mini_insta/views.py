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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404

class MiniInstaLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        return reverse("login")

    def get_my_profile(self):
        # Use first() so admin (who may have many profiles) won't crash your app.
        p = Profile.objects.filter(user=self.request.user).first()
        if not p:
            raise Http404("No profile associated with this user.")
        return p

class PostOwnerRequiredMixin(UserPassesTestMixin):
    """Allow access only if the logged-in user owns the post."""

    def test_func(self):
        post = self.get_object()
        return post.profile.user == self.request.user

class MyProfileDetailView(MiniInstaLoginRequiredMixin, DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.get_my_profile()

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

class CreatePostView(MiniInstaLoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.get_my_profile()
        return context

    def form_valid(self, form):
        form.instance.profile = self.get_my_profile()
        response = super().form_valid(form)

        files = self.request.FILES.getlist("files")
        for f in files:
            Photo.objects.create(post=self.object, image_file=f)

        return response

class UpdateProfileView(MiniInstaLoginRequiredMixin, UpdateView):
    """Update an existing Profile record."""
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"
    def get_object(self, queryset=None):
        return Profile.objects.filter(user=self.request.user).first()

class DeletePostView(MiniInstaLoginRequiredMixin, PostOwnerRequiredMixin, DeleteView):
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
        # after delete, go back to the author's profile page
        return self.object.profile.get_absolute_url()


class UpdatePostView(LoginRequiredMixin, PostOwnerRequiredMixin, UpdateView):
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

class PostFeedListView(MiniInstaLoginRequiredMixin, ListView):
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.profile = self.get_my_profile()
        return self.profile.get_post_feed()

    def get_context_data(self, **kwargs):
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

class SearchView(MiniInstaLoginRequiredMixin, ListView):
    template_name = "mini_insta/search_results.html"
    context_object_name = "posts"

    def dispatch(self, request, *args, **kwargs):
        if "query" not in request.GET:
            profile = self.get_my_profile()
            return render(request, "mini_insta/search.html", {"profile": profile})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET.get("query", "").strip()
        if not q:
            return Post.objects.none()
        return Post.objects.filter(caption__icontains=q).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_my_profile()
        q = self.request.GET.get("query", "").strip()

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
        context["posts"] = self.get_queryset()
        context["profiles"] = matching_profiles
        return context
