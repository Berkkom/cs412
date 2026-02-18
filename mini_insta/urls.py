# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/18/2026
# Description: URL routes for mini_insta (profile list and profile detail pages).

from django.urls import path
from .views import ProfileListView, ProfileDetailView

urlpatterns = [
    path("", ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>", ProfileDetailView.as_view(), name="show_profile"),
]
