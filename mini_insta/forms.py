# File: forms.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/20/2026
# Description: Django forms for mini_insta, including CreatePostForm for creating a Post and one Photo URL.

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