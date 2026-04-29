# File: admin.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/19/2026
# Description: Django admin configuration for the music rating application.
# Registers all models with customized list displays, search fields,
# and filters for easy data management through the admin panel.

from django.contrib import admin
from .models import Artist, Album, Song, Profile, Rating, Comment

class ArtistAdmin(admin.ModelAdmin):
    '''Admin configuration for the Artist model.'''
    list_display = ('name', 'musicbrainz_id')
    search_fields = ('name',)

class AlbumAdmin(admin.ModelAdmin):
    '''Admin configuration for the Album model.'''
    list_display = ('title', 'artist', 'release_date')
    search_fields = ('title',)
    list_filter = ('artist',)

class SongAdmin(admin.ModelAdmin):
    '''Admin configuration for the Song model.'''
    list_display = ('title', 'album', 'track_number', 'duration_ms')
    search_fields = ('title',)
    list_filter = ('album',)

class ProfileAdmin(admin.ModelAdmin):
    '''Admin configuration for the Profile model.'''
    list_display = ('display_name', 'user', 'country')
    search_fields = ('display_name', 'user__username')

class RatingAdmin(admin.ModelAdmin):
    '''Admin configuration for the Rating model.'''
    list_display = ('user', 'song', 'score', 'created_at')
    search_fields = ('user__username', 'song__title')
    list_filter = ('score',)

class CommentAdmin(admin.ModelAdmin):
    '''Admin configuration for the Comment model.'''
    list_display = ('user', 'rating', 'created_at')
    search_fields = ('user__username', 'text')

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Comment, CommentAdmin)