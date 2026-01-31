# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 1/30/2026
# Description: URL routes for the quotes app. Maps URL patterns to view
# functions for the home/random quote page, show-all page, and about page.

"""Define URL patterns for the quotes application."""
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    # Main page: displays a random quote and image.
    path('', views.quote, name='home'),       

    # Alternate route: same behavior as the main page.    
    path('quote/', views.quote, name='quote'),   

    # Ancillary page: displays all quotes and all images.
    path('show_all/', views.show_all, name='show_all'),

    # About page: describes the quoted person and the creator of the site.
    path('about/', views.about, name='about'),
]
