# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/19/2026
# Description: URL configuration for the music rating application.
# Maps URLs to views for artists, albums, songs, profiles, ratings,
# authentication, and MusicBrainz search.

from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Search & Browse URLs
    path('', views.search, name='search'),
    path('search/artist/<str:artist_mbid>/', views.browse_artist, name='browse_artist'),
    path('search/artist/<str:artist_mbid>/album/<str:release_group_mbid>/', views.browse_album, name='browse_album'),
    path('import/', views.import_song, name='import_song'),

    # Artist URLs
    path('artist/<int:pk>/', views.ArtistDetailView.as_view(), name='artist_detail'),

    # Album URLs
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),

    # Song URLs
    path('song/<int:pk>/', views.SongDetailView.as_view(), name='song_detail'),

    # Profile URLs
    path('profiles/', views.ProfileListView.as_view(), name='profile_list'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),

    # Rating URLs
    path('rating/<int:pk>/', views.RatingDetailView.as_view(), name='rating_detail'),
    path('song/<int:pk>/rate/', views.rate_song, name='rate_song'),
    path('rating/<int:pk>/delete/', views.delete_rating, name='delete_rating'),

    # Feed URL
    path('feed/', views.feed, name='feed'),

    # Like URL
    path('rating/<int:pk>/like/', views.toggle_like, name='toggle_like'),

    # Comment URLs
    path('rating/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Follow URL
    path('profile/<int:pk>/follow/', views.toggle_follow, name='toggle_follow'),
]