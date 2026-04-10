# File: forms.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/24/2026
# Description: Django forms for mini_insta (creating posts, updating profiles).

from django import forms
from .models import *

class CreatePostForm(forms.ModelForm):
    """Form to create a Post (caption only)."""

    class Meta:
        model = Post
        fields = ["caption"]  

class UpdateProfileForm(forms.ModelForm):
    """Form to update a Profile (excluding username and join_date)."""

    class Meta:
        model = Profile
        fields = ["display_name", "profile_image_url", "bio_text"]

class CreateProfileForm(forms.ModelForm):
    """Form to create a Profile (User is assigned programmatically)."""

    class Meta:
        model = Profile
        fields = ["username", "display_name", "bio_text", "profile_image_url"]  # use image_url if that's your field name
        labels = {
            "profile_image_url": "Image URL",
        }