# File: models.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/18/2026
# Description: Data models for the mini_insta app (e.g., Profile).

from django.db import models

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