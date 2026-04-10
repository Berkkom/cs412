# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/24/2026
# Description: URL routes for mini_insta (profiles, posts, feed, followers/following,
# search, create/update/delete operations).

from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path("", ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>", ProfileDetailView.as_view(), name="show_profile"),
    path("post/<int:pk>", PostDetailView.as_view(), name="show_post"),
    path("profile/<int:pk>/followers", ShowFollowersDetailView.as_view(), name="show_followers"),
    path("profile/<int:pk>/following", ShowFollowingDetailView.as_view(), name="show_following"),
    path("login/", auth_views.LoginView.as_view(template_name="mini_insta/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="logout_confirmation"), name="logout"),
    path("logout_confirmation/", TemplateView.as_view(template_name="mini_insta/logged_out.html"), name="logout_confirmation"),
    path("profile", MyProfileDetailView.as_view(), name="my_profile"),
    path("profile/create_post", CreatePostView.as_view(), name="create_post"),
    path("profile/update", UpdateProfileView.as_view(), name="update_profile"),
    path("profile/feed", PostFeedListView.as_view(), name="show_feed"),
    path("profile/search", SearchView.as_view(), name="search"),
    path("post/<int:pk>/delete", DeletePostView.as_view(), name="delete_post"),
    path("post/<int:pk>/update", UpdatePostView.as_view(), name="update_post"),
    path("create_profile", CreateProfileView.as_view(), name="create_profile"),
    path("profile/<int:pk>/follow", FollowProfileView.as_view(), name="follow_profile"),
path("profile/<int:pk>/delete_follow", UnfollowProfileView.as_view(), name="delete_follow"),
path("post/<int:pk>/like", LikePostView.as_view(), name="like_post"),
path("post/<int:pk>/delete_like", UnlikePostView.as_view(), name="delete_like"),
]

