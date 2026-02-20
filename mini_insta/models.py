# File: models.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/20/2026
# Description: Data models for mini_insta (Profile, Post, Photo) and helper methods to access related objects.

from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Profile(models.Model):
    """Model representing one mini_insta user profile."""
    username = models.TextField(blank=False)
    display_name = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=False)
    bio_text = models.TextField(blank=False)
    join_date = models.DateField(auto_now=True)

    def __str__(self):
        """Return a simple string representation of this object."""
        return f'{self.username} created {self.join_date}'
    
    def get_all_posts(self):
        """Return a QuerySet of all Posts for this Profile (newest first)."""
        return Post.objects.filter(profile=self).order_by("-timestamp")

class Post(models.Model):
    """Model representing an Instagram-style post."""

    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    caption = models.TextField(blank=True)

    def __str__(self):
        """Return a simple string representation of this Post."""
        return f"Post {self.pk} by {self.profile.username}"

    def get_all_photos(self):
        """Return a QuerySet of all Photos for this Post (ordered by timestamp)."""
        return Photo.objects.filter(post=self).order_by("timestamp")
    
    def get_absolute_url(self):
        """Return the URL to view this post."""
        return reverse("show_post", kwargs={"pk": self.pk})

class Photo(models.Model):
    """Model representing a photo associated with a Post."""

    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return a simple string representation of this Photo."""
        return f"Photo {self.pk} for Post {self.post.pk}"