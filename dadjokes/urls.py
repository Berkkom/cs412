# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: URL configuration for the dadjokes app. Maps URL patterns
# to template-based views for HTML rendering and REST API views for JSON
# responses. Includes endpoints for jokes, pictures, and random selections.

from django.urls import path
from . import views

urlpatterns = [
    # ── Template-based URLs ──────────────────────────────
    path('', views.random_joke_and_picture, name='random_home'),
    path('random', views.random_joke_and_picture, name='random'),
    path('jokes', views.all_jokes, name='all_jokes'),
    path('joke/<int:pk>', views.one_joke, name='one_joke'),
    path('pictures', views.all_pictures, name='all_pictures'),
    path('picture/<int:pk>', views.one_picture, name='one_picture'),

    # ── REST API URLs ────────────────────────────────────
    path('api/', views.api_random_joke, name='api_random_home'),
    path('api/random', views.api_random_joke, name='api_random'),
    path('api/jokes', views.api_all_jokes, name='api_all_jokes'),
    path('api/joke/<int:pk>', views.api_one_joke, name='api_one_joke'),
    path('api/pictures', views.api_all_pictures, name='api_all_pictures'),
    path('api/picture/<int:pk>', views.api_one_picture, name='api_one_picture'),
    path('api/random_picture', views.api_random_picture, name='api_random_picture'),
]