# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 3/19/2026
# Description: URL patterns for the voter_analytics application.

from django.urls import path
from .views import VoterListView, VoterDetailView, GraphListView

urlpatterns = [
    path("", VoterListView.as_view(), name="voters"),
    path("voter/<int:pk>/", VoterDetailView.as_view(), name="voter"),
    path("graphs/", GraphListView.as_view(), name="graphs"),
]