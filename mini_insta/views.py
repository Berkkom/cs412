# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/24/2026
# Description: Class-based views for mini_insta, including profile/post display,
# creating/updating/deleting posts, updating profiles, follower/following pages,
# post feed, and search.


from django.views.generic import ListView, DetailView, TemplateView
from .models import Profile, Post, Photo, Follow, Like
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import *
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            my_profile = Profile.objects.filter(user=self.request.user).first()
            context["my_profile"] = my_profile

            # Only show follow button if not viewing your own profile
            context["can_follow"] = (my_profile is not None and my_profile.pk != self.object.pk)

            # True/False: am I following this profile?
            if context["can_follow"]:
                context["is_following"] = Follow.objects.filter(
                    follower_profile=my_profile,
                    profile=self.object
                ).exists()
            else:
                context["is_following"] = False

        return context

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
        return self.get_my_profile()

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


class UpdatePostView(MiniInstaLoginRequiredMixin, PostOwnerRequiredMixin, UpdateView):
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
        context["profile"] = self.object.profile  # post owner

        if self.request.user.is_authenticated:
            my_profile = Profile.objects.filter(user=self.request.user).first()
            context["my_profile"] = my_profile

            context["can_like"] = (my_profile is not None and my_profile.pk != self.object.profile.pk)

            if context["can_like"]:
                context["is_liked"] = Like.objects.filter(post=self.object, profile=my_profile).exists()
            else:
                context["is_liked"] = False

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

class CreateProfileView(CreateView):
    """Create a new Django User and a new Profile in one submission."""
    model = Profile
    form_class = CreateProfileForm
    template_name = "mini_insta/create_profile_form.html"

    def get_context_data(self, **kwargs):
        """Add a UserCreationForm to the context so the template can show both forms."""
        context = super().get_context_data(**kwargs)
        context["user_form"] = context.get("user_form", UserCreationForm())
        return context

    def form_valid(self, form):
        """
        Create the User first, log them in, attach the user to the Profile,
        then save the Profile via the normal CreateView flow.
        """
        user_form = UserCreationForm(self.request.POST)

        if not user_form.is_valid():
            # Re-render the page showing both forms + user_form errors
            return self.render_to_response(self.get_context_data(form=form, user_form=user_form))

        user = user_form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")

        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        """After creation, go to the new user's profile page."""
        return self.object.get_absolute_url()

class FollowProfileView(MiniInstaLoginRequiredMixin, TemplateView):
    """Logged-in user follows another Profile."""
    def dispatch(self, request, *args, **kwargs):
        me = self.get_my_profile()
        other = Profile.objects.get(pk=kwargs["pk"])

        # don't allow self-follow
        if me.pk != other.pk:
            Follow.objects.get_or_create(profile=other, follower_profile=me)

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return []  # no template; we redirect

    def get(self, request, *args, **kwargs):
        return redirect("show_profile", pk=kwargs["pk"])


class UnfollowProfileView(MiniInstaLoginRequiredMixin, TemplateView):
    """Logged-in user unfollows another Profile."""
    def dispatch(self, request, *args, **kwargs):
        me = self.get_my_profile()
        other = Profile.objects.get(pk=kwargs["pk"])
        Follow.objects.filter(profile=other, follower_profile=me).delete()
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return []

    def get(self, request, *args, **kwargs):
        return redirect("show_profile", pk=kwargs["pk"])


class LikePostView(MiniInstaLoginRequiredMixin, TemplateView):
    """Logged-in user likes a Post."""
    def dispatch(self, request, *args, **kwargs):
        me = self.get_my_profile()
        post = Post.objects.get(pk=kwargs["pk"])

        # don't allow liking own post
        if post.profile_id != me.pk:
            Like.objects.get_or_create(post=post, profile=me)

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return []

    def get(self, request, *args, **kwargs):
        return redirect("show_post", pk=kwargs["pk"])


class UnlikePostView(MiniInstaLoginRequiredMixin, TemplateView):
    """Logged-in user unlikes a Post."""
    def dispatch(self, request, *args, **kwargs):
        me = self.get_my_profile()
        post = Post.objects.get(pk=kwargs["pk"])
        Like.objects.filter(post=post, profile=me).delete()
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return []

    def get(self, request, *args, **kwargs):
        return redirect("show_post", pk=kwargs["pk"])