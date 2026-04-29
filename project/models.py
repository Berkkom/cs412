# File: models.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/19/2026
# Description: Data models for a social music rating application where users can
# browse artists, albums, and songs, rate songs on a 1-10 scale, write reviews,
# follow other users, like and comment on ratings, and view statistics.

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class Artist(models.Model):
    '''
    Represents a music artist. This is the standalone model with no foreign keys.
    Artist data is sourced from the MusicBrainz API.
    '''
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    musicbrainz_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        '''Return a string representation of the Artist.'''
        return self.name

    def get_absolute_url(self):
        '''Return the URL to display this Artist.'''
        return reverse('project:artist_detail', kwargs={'pk': self.pk})

class Album(models.Model):
    '''
    Represents a music album. Requires an Artist (Foreign Key).
    Album cover art is fetched at render time from the MusicBrainz 
    Cover Art Archive using the stored musicbrainz_id.
    '''
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    release_date = models.DateField(null=True, blank=True)
    musicbrainz_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        '''Return a string representation of the Album.'''
        return f"{self.title} - {self.artist.name}"

    def get_absolute_url(self):
        '''Return the URL to display this Album.'''
        return reverse('project:album_detail', kwargs={'pk': self.pk})

class Song(models.Model):
    '''
    Represents a single song/track. Requires an Album (Foreign Key).
    '''
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    track_number = models.PositiveIntegerField()
    duration_ms = models.PositiveIntegerField(help_text="Duration in milliseconds")
    musicbrainz_id = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['track_number']

    def __str__(self):
        '''Return a string representation of the Song.'''
        return f"{self.title} - {self.album.artist.name}"

    def get_absolute_url(self):
        '''Return the URL to display this Song.'''
        return reverse('project:song_detail', kwargs={'pk': self.pk})

    def get_average_rating(self):
        '''Calculate and return the average rating for this song.'''
        avg = self.ratings.aggregate(avg_score=models.Avg('score'))['avg_score']
        return round(avg, 1) if avg else None

    def get_rating_count(self):
        '''Return the total number of ratings for this song.'''
        return self.ratings.count()

class Profile(models.Model):
    '''
    Extends Django's built-in User model with additional profile information.
    Each user has one Profile (One-to-One relationship via Foreign Key).
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='music_profile')
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self):
        '''Return a string representation of the Profile.'''
        return f"{self.display_name} (@{self.user.username})"

    def get_absolute_url(self):
        '''Return the URL to display this Profile.'''
        return reverse('project:profile_detail', kwargs={'pk': self.pk})

    def get_rating_count(self):
        '''Return the total number of ratings by this user.'''
        return Rating.objects.filter(user=self.user).count()

    def get_follower_count(self):
        '''Return the number of followers this profile has.'''
        return self.followers.count()

    def get_following_count(self):
        '''Return the number of profiles this user follows.'''
        return self.following.count()

class Rating(models.Model):
    '''
    Represents a user's rating of a song on a scale of 1-10.
    Requires both a User and a Song (two Foreign Keys).
    Includes optional review text and a likes system via ManyToManyField.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='ratings')
    score = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        help_text="Rating from 1.0 to 10.0"
    )
    review_text = models.TextField(blank=True)
    likes = models.ManyToManyField(User, related_name='liked_ratings', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-created_at']

    def __str__(self):
        '''Return a string representation of the Rating.'''
        return f"{self.user.username} rated {self.song.title}: {self.score}/10"

    def get_absolute_url(self):
        '''Return the URL to display this Rating.'''
        return reverse('project:rating_detail', kwargs={'pk': self.pk})

    def get_like_count(self):
        '''Return the number of likes on this rating.'''
        return self.likes.count()

class Comment(models.Model):
    '''
    Represents a comment on a Rating. Requires both a User and a Rating
    (two Foreign Keys). Allows users to discuss each other's song ratings.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        '''Return a string representation of the Comment.'''
        return f"{self.user.username} commented on {self.rating.song.title}"