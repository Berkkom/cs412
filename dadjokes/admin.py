# File: admin.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: Admin configuration for the dadjokes app. Registers the
# Joke and Picture models with the Django admin site for easy management.

from django.contrib import admin
from .models import Joke, Picture

@admin.register(Joke)
class JokeAdmin(admin.ModelAdmin):
    """Admin interface configuration for the Joke model."""
    list_display = ('text', 'contributor', 'created')
    ordering = ('-created',)

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    """Admin interface configuration for the Picture model."""
    list_display = ('image_url', 'contributor', 'created')
    ordering = ('-created',)