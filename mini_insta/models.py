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
    image_url = models.URLField(max_length=500, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    image_file = models.ImageField(upload_to="mini_insta_photos/", blank=True, null=True)

    def __str__(self):
        """Return a simple string representation showing how this photo is stored."""
        if self.image_url:
            return f"Photo {self.pk} (URL) for Post {self.post.pk}"
        
        if self.image_file:
            return f"Photo {self.pk} (FILE) for Post {self.post.pk}"
        
        return f"Photo {self.pk} (NO IMAGE) for Post {self.post.pk}"
    
    def get_image_url(self):
        """
        Return a usable URL for the photo image.
        Prefer image_url if provided; otherwise use the uploaded file URL.
        """
        if self.image_url:
            return self.image_url
        
        if self.image_file:
            return self.image_file.url
        
        return ""