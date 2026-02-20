# File: forms.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/20/2026
# Description: Django forms for mini_insta, including CreatePostForm for creating a Post and one Photo URL.

from django import forms
from .models import *


class CreatePostForm(forms.ModelForm):
    """Form to create a Post (caption) plus one Photo (image_url)."""

    image_url = forms.URLField(label="Image URL", required=True)

    class Meta:
        model = Post
        fields = ["caption"]  