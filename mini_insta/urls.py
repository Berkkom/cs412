# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/17/2026
from django.urls import path
from .views import ProfileListView

urlpatterns = [
    path('', ProfileListView.as_view(),name='show_all_profiles')
]