# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/19/2026
# Description: Django views for the music rating application.
# Includes authentication (login, signup, logout), MusicBrainz search,
# and generic class-based views for displaying data.

import requests
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Artist, Album, Song, Profile, Rating, Comment
from .forms import RegisterForm

class ArtistListView(ListView):
    '''Display a searchable list of artists in the local database.'''
    model = Artist
    template_name = 'project/artist_list.html'
    context_object_name = 'artists'

    def get_queryset(self):
        '''Filter artists by search query if provided.'''
        queryset = Artist.objects.all()
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
        # Annotate with average rating and rating count
        from django.db.models import Avg, Count
        queryset = queryset.annotate(
            avg_rating=Avg('albums__songs__ratings__score'),
            rating_count=Count('albums__songs__ratings'),
        ).order_by('-rating_count')
        return queryset

    def get_context_data(self, **kwargs):
        '''Add the search query to the context.'''
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ArtistDetailView(DetailView):
    '''Display details for a single artist, including ratings and reviews.'''
    model = Artist
    template_name = 'project/artist_detail.html'
    context_object_name = 'artist'

    def get_context_data(self, **kwargs):
        '''Add artist stats and all ratings to the context.'''
        context = super().get_context_data(**kwargs)
        from django.db.models import Avg, Count
        artist = self.object

        # Get all ratings for this artist's songs
        artist_ratings = Rating.objects.filter(
            song__album__artist=artist
        ).select_related('user', 'song', 'song__album').order_by('-created_at')

        # Calculate artist-level stats
        stats = artist_ratings.aggregate(
            avg_rating=Avg('score'),
            total_ratings=Count('id'),
        )

        context['ratings'] = artist_ratings
        context['avg_rating'] = round(stats['avg_rating'], 1) if stats['avg_rating'] else None
        context['total_ratings'] = stats['total_ratings']

        # Get albums with rating stats
        annotated_albums = Album.objects.filter(artist=artist).annotate(
            album_avg=Avg('songs__ratings__score'),
            album_count=Count('songs__ratings'),
        ).order_by('release_date')
        context['annotated_albums'] = annotated_albums

        # Aggregate ratings by country for the world map
        import json
        country_data = Rating.objects.filter(
            song__album__artist=artist,
            user__music_profile__country__isnull=False,
        ).exclude(
            user__music_profile__country='',
        ).values(
            'user__music_profile__country'
        ).annotate(
            avg_score=Avg('score'),
            count=Count('id'),
        )
        context['country_data_json'] = json.dumps([
            {'country': c['user__music_profile__country'], 'avg': float(round(c['avg_score'], 1)), 'count': c['count']}
            for c in country_data
        ])

        return context

class AlbumDetailView(DetailView):
    '''Display details for a single album, including its songs and reviews.'''
    model = Album
    template_name = 'project/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        '''Add album stats, ratings, and country data for the map.'''
        context = super().get_context_data(**kwargs)
        from django.db.models import Avg, Count
        album = self.object

        # Get all ratings for this album's songs
        album_ratings = Rating.objects.filter(
            song__album=album
        ).select_related('user', 'song').order_by('-created_at')

        # Calculate album-level stats
        stats = album_ratings.aggregate(
            avg_rating=Avg('score'),
            total_ratings=Count('id'),
        )

        # Aggregate ratings by country for the world map
        import json
        country_data = Rating.objects.filter(
            song__album=album,
            user__music_profile__country__isnull=False,
        ).exclude(
            user__music_profile__country='',
        ).values(
            'user__music_profile__country'
        ).annotate(
            avg_score=Avg('score'),
            count=Count('id'),
        )

        context['ratings'] = album_ratings
        context['avg_rating'] = round(stats['avg_rating'], 1) if stats['avg_rating'] else None
        context['total_ratings'] = stats['total_ratings']
        context['country_data_json'] = json.dumps([
            {'country': c['user__music_profile__country'], 'avg': float(round(c['avg_score'], 1)), 'count': c['count']}
            for c in country_data
        ])
        return context

class SongDetailView(DetailView):
    '''Display details for a single song, including its ratings.'''
    model = Song
    template_name = 'project/song_detail.html'
    context_object_name = 'song'

    def get_context_data(self, **kwargs):
        '''Add the user's existing rating (if any) to the context.'''
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user_rating = Rating.objects.filter(
                user=self.request.user,
                song=self.object,
            ).first()
            context['user_rating'] = user_rating
        return context

class ProfileListView(ListView):
    '''Display a searchable list of all user profiles.'''
    model = Profile
    template_name = 'project/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        '''Filter profiles by search query if provided.'''
        queryset = Profile.objects.all()
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(display_name__icontains=query) |
                Q(user__username__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        '''Add the search query to the context.'''
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ProfileDetailView(DetailView):
    '''Display details for a single user profile, including their ratings.'''
    model = Profile
    template_name = 'project/profile_detail.html'
    context_object_name = 'profile'

class RatingDetailView(DetailView):
    '''Display details for a single rating, including its comments.'''
    model = Rating
    template_name = 'project/rating_detail.html'
    context_object_name = 'rating'

# ─── Authentication Views ───────────────────────────────────────────

class CustomLoginView(LoginView):
    '''Login view that redirects to the artist list after login.'''
    template_name = 'project/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        '''Redirect to the search page after successful login.'''
        return reverse_lazy('project:search')

class CustomLogoutView(LogoutView):
    '''Logout view that redirects to the login page.'''
    next_page = reverse_lazy('project:login')

class RegisterView(CreateView):
    '''Registration view that creates a new user and their profile.'''
    model = User
    form_class = RegisterForm
    template_name = 'project/register.html'
    success_url = reverse_lazy('project:search')

    def form_valid(self, form):
        '''After creating the user, create a Profile and log them in.'''
        from django.contrib.auth import login
        response = super().form_valid(form)
        Profile.objects.create(
            user=self.object,
            display_name=form.cleaned_data.get('display_name', self.object.username),
            country=form.cleaned_data.get('country', ''),
        )
        login(self.request, self.object)
        return redirect('project:search')

# ─── MusicBrainz Search Views ──────────────────────────────────────

MUSICBRAINZ_BASE = 'https://musicbrainz.org/ws/2'
MUSICBRAINZ_HEADERS = {
    'User-Agent': 'MusicRater/1.0 (berkkom@bu.edu)',
    'Accept': 'application/json',
}
import time

def search(request):
    '''
    Search for artists using the MusicBrainz API.
    Users click an artist to browse their albums, then tracks, then rate.

    Parameters:
    - request: the HTTP request object; GET parameter 'q' contains the search query.
    '''
    query = request.GET.get('q', '').strip()
    artists = []

    if query:
        try:
            response = requests.get(
                f'{MUSICBRAINZ_BASE}/artist',
                params={'query': query, 'fmt': 'json', 'limit': 10},
                headers=MUSICBRAINZ_HEADERS,
            )
            if response.status_code == 200:
                for artist in response.json().get('artists', []):
                    artists.append({
                        'name': artist.get('name', 'Unknown'),
                        'id': artist.get('id', ''),
                        'type': artist.get('type', ''),
                        'country': artist.get('country', ''),
                        'disambiguation': artist.get('disambiguation', ''),
                    })
        except requests.RequestException:
            pass

    context = {
        'query': query,
        'artists': artists,
    }

    # Look up local rating stats for each artist
    if artists:
        from django.db.models import Avg, Count
        artist_mbids = [a['id'] for a in artists]
        local_artists = Artist.objects.filter(musicbrainz_id__in=artist_mbids).annotate(
            avg_rating=Avg('albums__songs__ratings__score'),
            rating_count=Count('albums__songs__ratings'),
        )
        artist_stats = {
            a.musicbrainz_id: {'avg': round(a.avg_rating, 1) if a.avg_rating else None, 'count': a.rating_count}
            for a in local_artists
        }
        for artist in artists:
            stats = artist_stats.get(artist['id'], {})
            artist['avg_rating'] = stats.get('avg', None)
            artist['rating_count'] = stats.get('count', 0)

    return render(request, 'project/search.html', context)

def browse_artist(request, artist_mbid):
    '''
    Browse albums for a given artist using the MusicBrainz API.
    Fetches official studio albums (release-groups) and displays them
    for the user to click and browse tracks.

    Parameters:
    - request: the HTTP request object.
    - artist_mbid: the MusicBrainz ID of the artist to browse.
    '''
    albums = []
    artist_name = ''

    try:
        # First, get the artist name
        response = requests.get(
            f'{MUSICBRAINZ_BASE}/artist/{artist_mbid}',
            params={'fmt': 'json'},
            headers=MUSICBRAINZ_HEADERS,
        )
        if response.status_code == 200:
            artist_name = response.json().get('name', 'Unknown')

        time.sleep(1)  # Respect MusicBrainz rate limit (1 req/sec)

        # Fetch release-groups (albums) for this artist
        response = requests.get(
            f'{MUSICBRAINZ_BASE}/release-group',
            params={
                'artist': artist_mbid,
                'type': 'album',
                'fmt': 'json',
                'limit': 50,
            },
            headers=MUSICBRAINZ_HEADERS,
        )
        if response.status_code == 200:
            data = response.json()
            for rg in data.get('release-groups', []):
                # Filter out compilations and live albums
                secondary_types = [t.lower() for t in rg.get('secondary-types', [])]
                if 'compilation' in secondary_types or 'live' in secondary_types:
                    continue

                albums.append({
                    'title': rg.get('title', 'Unknown'),
                    'id': rg.get('id', ''),
                    'release_date': rg.get('first-release-date', ''),
                    'primary_type': rg.get('primary-type', ''),
                })

            # Sort by release date (earliest first)
            albums.sort(key=lambda x: x.get('release_date', '') or 'zzzz')

    except requests.RequestException:
        pass

    # Check if this artist exists in the local database (has been rated)
    from django.db.models import Avg, Count
    local_artist = Artist.objects.filter(musicbrainz_id=artist_mbid).annotate(
        avg_rating=Avg('albums__songs__ratings__score'),
        rating_count=Count('albums__songs__ratings'),
    ).first()

    # Look up local rating stats for each album
    album_mbids = [a['id'] for a in albums]
    local_albums = Album.objects.filter(musicbrainz_id__in=album_mbids).annotate(
        avg_rating=Avg('songs__ratings__score'),
        rating_count=Count('songs__ratings'),
    )
    album_stats = {a.musicbrainz_id: {'avg': round(a.avg_rating, 1) if a.avg_rating else None, 'count': a.rating_count} for a in local_albums}

    # Attach stats to album results
    for album in albums:
        stats = album_stats.get(album['id'], {})
        album['avg_rating'] = stats.get('avg', None)
        album['rating_count'] = stats.get('count', 0)

    context = {
        'artist_name': artist_name,
        'artist_mbid': artist_mbid,
        'albums': albums,
        'local_artist': local_artist,
    }
    return render(request, 'project/browse_artist.html', context)

def browse_album(request, artist_mbid, release_group_mbid):
    '''
    Browse tracks for a given album using the MusicBrainz API.
    Fetches the tracklist from a specific release and displays songs
    for the user to import and rate.

    Parameters:
    - request: the HTTP request object.
    - artist_mbid: the MusicBrainz ID of the artist.
    - release_group_mbid: the MusicBrainz release-group ID of the album.
    '''
    tracks = []
    album_title = ''
    artist_name = ''
    release_date = ''

    try:
        # Get the release-group info (album title, date)
        response = requests.get(
            f'{MUSICBRAINZ_BASE}/release-group/{release_group_mbid}',
            params={
                'fmt': 'json',
                'inc': 'artist-credits',
            },
            headers=MUSICBRAINZ_HEADERS,
        )
        if response.status_code == 200:
            rg_data = response.json()
            album_title = rg_data.get('title', 'Unknown')
            release_date = rg_data.get('first-release-date', '')
            artist_credits = rg_data.get('artist-credit', [])
            if artist_credits:
                artist_name = artist_credits[0].get('name', 'Unknown')

        time.sleep(1)  # Respect MusicBrainz rate limit

        # Find an official release for this release-group to get the tracklist
        response = requests.get(
            f'{MUSICBRAINZ_BASE}/release',
            params={
                'release-group': release_group_mbid,
                'status': 'official',
                'fmt': 'json',
                'limit': 10,
            },
            headers=MUSICBRAINZ_HEADERS,
        )

        release_id = ''
        if response.status_code == 200:
            releases = response.json().get('releases', [])
            if releases:
                # Pick the first official release
                release_id = releases[0].get('id', '')

        if release_id:
            time.sleep(1)  # Respect rate limit

            # Fetch the tracklist for this release
            response = requests.get(
                f'{MUSICBRAINZ_BASE}/release/{release_id}',
                params={
                    'fmt': 'json',
                    'inc': 'recordings',
                },
                headers=MUSICBRAINZ_HEADERS,
            )
            if response.status_code == 200:
                release_data = response.json()
                for medium in release_data.get('media', []):
                    for track in medium.get('tracks', []):
                        recording = track.get('recording', {})
                        tracks.append({
                            'title': recording.get('title', 'Unknown'),
                            'recording_id': recording.get('id', ''),
                            'track_number': track.get('position', 0),
                            'duration': recording.get('length', 0),
                        })

    except requests.RequestException:
        pass

    # Check if this album exists in the local database (has been rated)
    from django.db.models import Avg, Count
    local_album = Album.objects.filter(musicbrainz_id=release_group_mbid).annotate(
        avg_rating=Avg('songs__ratings__score'),
        rating_count=Count('songs__ratings'),
    ).first()

    # Look up local rating stats for each track
    track_mbids = [t['recording_id'] for t in tracks]
    local_songs = Song.objects.filter(musicbrainz_id__in=track_mbids).annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings'),
    )
    song_stats = {s.musicbrainz_id: {'avg': round(s.avg_rating, 1) if s.avg_rating else None, 'count': s.rating_count} for s in local_songs}

    # Fallback: also look up by title + album for songs imported with different IDs
    if local_album:
        title_songs = Song.objects.filter(album=local_album).annotate(
            avg_rating=Avg('ratings__score'),
            rating_count=Count('ratings'),
        )
        song_stats_by_title = {s.title.lower(): {'avg': round(s.avg_rating, 1) if s.avg_rating else None, 'count': s.rating_count} for s in title_songs}
    else:
        song_stats_by_title = {}

    # Attach stats to track results
    for track in tracks:
        stats = song_stats.get(track['recording_id'], {})
        # Fallback to title match if no ID match
        if not stats.get('avg'):
            stats = song_stats_by_title.get(track['title'].lower(), {})
        track['avg_rating'] = stats.get('avg', None)
        track['rating_count'] = stats.get('count', 0)

    context = {
        'artist_name': artist_name,
        'artist_mbid': artist_mbid,
        'album_title': album_title,
        'release_group_mbid': release_group_mbid,
        'release_date': release_date,
        'tracks': tracks,
        'local_album': local_album,
    }
    return render(request, 'project/browse_album.html', context)

def import_song(request):
    '''
    Import a song from MusicBrainz into the local database.
    Creates Artist, Album, and Song records if they don't already exist.
    Redirects to the song detail page after import.

    Parameters:
    - request: the HTTP request object; POST data contains song, artist,
      and album details from MusicBrainz.
    '''
    if request.method == 'POST':
        # Get data from the form
        song_title = request.POST.get('song_title', '')
        song_id = request.POST.get('song_id', '')
        artist_name = request.POST.get('artist_name', '')
        artist_id = request.POST.get('artist_id', '')
        album_title = request.POST.get('album_title', '')
        release_group_id = request.POST.get('release_group_id', '')
        release_date = request.POST.get('release_date', '')
        duration = int(request.POST.get('duration', 0) or 0)
        track_number = int(request.POST.get('track_number', 1) or 1)

        # Create or get the Artist
        artist, _ = Artist.objects.get_or_create(
            musicbrainz_id=artist_id,
            defaults={'name': artist_name},
        )

        # Create or get the Album
        album, _ = Album.objects.get_or_create(
            musicbrainz_id=release_group_id,
            defaults={
                'title': album_title,
                'artist': artist,
                'release_date': release_date if release_date else None,
            },
        )

        # Create or get the Song
        song, _ = Song.objects.get_or_create(
            musicbrainz_id=song_id,
            defaults={
                'title': song_title,
                'album': album,
                'track_number': track_number,
                'duration_ms': duration,
            },
        )

        return redirect('project:song_detail', pk=song.pk)

    return redirect('project:search')

# ─── Rating Views ──────────────────────────────────────────────────

@login_required
def rate_song(request, pk):
    '''
    Create or update a rating for a song.
    If the user has already rated this song, updates the existing rating.
    Otherwise, creates a new rating.

    Parameters:
    - request: the HTTP request object; POST data contains 'score' and 'review_text'.
    - pk: the primary key of the Song to rate.
    '''
    song = get_object_or_404(Song, pk=pk)

    if request.method == 'POST':
        score_str = request.POST.get('score', '').strip()
        review_text = request.POST.get('review_text', '').strip()

        # Validate score
        try:
            score = Decimal(score_str)
            if score < 1 or score > 10:
                return redirect('project:song_detail', pk=song.pk)
        except (InvalidOperation, ValueError):
            return redirect('project:song_detail', pk=song.pk)

        # Create or update the rating
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            song=song,
            defaults={
                'score': score,
                'review_text': review_text,
            },
        )

        return redirect('project:song_detail', pk=song.pk)

    return redirect('project:song_detail', pk=song.pk)

@login_required
def delete_rating(request, pk):
    '''
    Delete a user's rating for a song.

    Parameters:
    - request: the HTTP request object.
    - pk: the primary key of the Rating to delete.
    '''
    rating = get_object_or_404(Rating, pk=pk, user=request.user)
    song_pk = rating.song.pk
    if request.method == 'POST':
        rating.delete()
    return redirect('project:song_detail', pk=song_pk)

# ─── Activity Feed ─────────────────────────────────────────────────

@login_required
def feed(request):
    '''
    Display an activity feed of recent ratings from users
    the logged-in user follows.

    Parameters:
    - request: the HTTP request object; GET parameter 'page' for pagination.
    '''
    profile = request.user.music_profile
    following_users = profile.following.values_list('user', flat=True)

    ratings = Rating.objects.filter(
        user__in=following_users
    ).select_related(
        'user', 'song', 'song__album', 'song__album__artist'
    ).prefetch_related('likes', 'comments').order_by('-created_at')

    # Paginate
    paginator = Paginator(ratings, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'ratings': page_obj,
    }
    return render(request, 'project/feed.html', context)

# ─── Like/Unlike ───────────────────────────────────────────────────

@login_required
def toggle_like(request, pk):
    '''
    Toggle a like on a rating. If the user has already liked it,
    removes the like. Otherwise, adds a like.

    Parameters:
    - request: the HTTP request object; POST data may contain 'next' URL for redirect.
    - pk: the primary key of the Rating to like/unlike.
    '''
    rating = get_object_or_404(Rating, pk=pk)
    if request.method == 'POST':
        if rating.likes.filter(id=request.user.id).exists():
            rating.likes.remove(request.user)
        else:
            rating.likes.add(request.user)
    # Redirect back to wherever the user came from
    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('project:rating_detail', pk=rating.pk)

# ─── Comments ──────────────────────────────────────────────────────

@login_required
def add_comment(request, pk):
    '''
    Add a comment to a rating.

    Parameters:
    - request: the HTTP request object; POST data contains 'text' for the comment.
    - pk: the primary key of the Rating to comment on.
    '''
    rating = get_object_or_404(Rating, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(
                user=request.user,
                rating=rating,
                text=text,
            )
    return redirect('project:rating_detail', pk=rating.pk)

@login_required
def delete_comment(request, pk):
    '''
    Delete a comment. Only the comment author can delete their own comment.

    Parameters:
    - request: the HTTP request object.
    - pk: the primary key of the Comment to delete.
    '''
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    rating_pk = comment.rating.pk
    if request.method == 'POST':
        comment.delete()
    return redirect('project:rating_detail', pk=rating_pk)

# ─── Follow/Unfollow ──────────────────────────────────────────────

@login_required
def toggle_follow(request, pk):
    '''
    Follow or unfollow a user profile. A user cannot follow themselves.

    Parameters:
    - request: the HTTP request object.
    - pk: the primary key of the Profile to follow/unfollow.
    '''
    target_profile = get_object_or_404(Profile, pk=pk)
    user_profile = request.user.music_profile

    if request.method == 'POST':
        if target_profile != user_profile:
            if user_profile.following.filter(pk=target_profile.pk).exists():
                user_profile.following.remove(target_profile)
            else:
                user_profile.following.add(target_profile)
    return redirect('project:profile_detail', pk=target_profile.pk)