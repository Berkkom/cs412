# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/20/2026
# Description: URL routes for mini_insta (profiles, posts, and creating new posts).

from django.urls import path
from .views import ProfileListView, ProfileDetailView, PostDetailView, CreatePostView, UpdateProfileView

urlpatterns = [
    path("", ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>", ProfileDetailView.as_view(), name="show_profile"),
    path("post/<int:pk>", PostDetailView.as_view(), name="show_post"),
    path("profile/<int:pk>/create_post", CreatePostView.as_view(), name="create_post"),
    path("profile/<int:pk>/update", UpdateProfileView.as_view(), name="update_profile"),
]
