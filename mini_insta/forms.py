from django import forms
from .models import *


class CreatePostForm(forms.ModelForm):
    """Form to create a Post (caption) plus one Photo (image_url)."""

    image_url = forms.URLField(label="Image URL", required=True)

    class Meta:
        model = Post
        fields = ["caption"]  