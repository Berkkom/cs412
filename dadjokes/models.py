# File: models.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: Data models for the dadjokes app. Defines the Joke and
# Picture models, each storing content, a contributor name, and a timestamp.

from django.db import models

class Joke(models.Model):
    """Represents a dad joke with its text, contributor, and creation timestamp."""
    text = models.TextField()
    contributor = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the Joke."""
        return f'"{self.text[:50]}..." by {self.contributor}'

class Picture(models.Model):
    """Represents a silly image/GIF with its URL, contributor, and creation timestamp."""
    image_url = models.URLField(max_length=500)
    contributor = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the Picture."""
        return f'Picture by {self.contributor} ({self.image_url[:50]}...)'