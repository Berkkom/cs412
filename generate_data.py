# File: generate_data.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/28/2026
# Description: Generates 100 users with profiles from different countries,
# each rating 4 specific songs. Fetches correct MusicBrainz recording IDs
# from the API to ensure consistency with the browse flow.
# Run with: python manage.py shell < generate_data.py

import os
import random
import time
import requests as http_requests
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs412.settings')

from django.contrib.auth.models import User
from project.models import Artist, Album, Song, Profile, Rating

# ─── MusicBrainz API Config ───────────────────────────────────────

MB_BASE = 'https://musicbrainz.org/ws/2'
MB_HEADERS = {
    'User-Agent': 'MusicRater/1.0 (berkkom@bu.edu)',
    'Accept': 'application/json',
}

# ─── Releases to fetch ─────────────────────────────────────────────

RELEASES = [
    {
        'release_id': '09ed5877-bb22-4a26-8ec7-c95e5ee70fd3',
        'target_song': 'Echoes',
    },
    {
        'release_id': '097a5c3e-9210-3264-8e94-d33fe65021d6',
        'target_song': 'Starless',
    },
    {
        'release_id': '90cf3f7e-a93a-45e0-8391-8863635ae0d5',
        'target_song': 'Reckoner',
    },
]

# ─── Countries with Weights ───────────────────────────────────────

COUNTRIES = [
    ('United States', 20), ('United Kingdom', 12), ('Germany', 8),
    ('France', 7), ('Canada', 6), ('Australia', 5), ('Brazil', 5),
    ('Japan', 4), ('Netherlands', 4), ('Italy', 4), ('Spain', 3),
    ('Sweden', 3), ('Turkey', 3), ('Mexico', 3), ('Argentina', 2),
    ('South Korea', 2), ('India', 2), ('Poland', 2), ('Ireland', 2),
    ('Norway', 1), ('Denmark', 1), ('Finland', 1), ('Belgium', 1),
    ('Switzerland', 1), ('Portugal', 1), ('South Africa', 1),
    ('New Zealand', 1), ('Chile', 1), ('Colombia', 1), ('Czech Republic', 1),
]
COUNTRY_POOL = []
for country, weight in COUNTRIES:
    COUNTRY_POOL.extend([country] * weight)

# ─── Review Templates ─────────────────────────────────────────────

REVIEWS = {
    'Echoes': [
        "A masterpiece of progressive rock.",
        "The sonar pings at the beginning are iconic.",
        "23 minutes of pure genius.",
        "This song changed my life.",
        "Pink Floyd at their most ambitious.",
        "The middle section is hauntingly beautiful.",
        "Greatest prog rock song ever written.",
        "Timeless. Absolutely timeless.",
        "The build-up is incredible.",
        "Pure art.",
    ],
    'Since I\'ve Been Loving You': [
        "Best blues rock song ever recorded.",
        "Bonham's drumming is unreal.",
        "Page's guitar solo gives me chills.",
        "Raw emotion in every note.",
        "The live versions are even better.",
        "Plant's vocals are out of this world.",
        "This is what real blues sounds like.",
        "Absolute perfection.",
        "The pain in this song is palpable.",
        "Led Zeppelin's finest moment.",
    ],
    'Starless': [
        "The greatest song ever written.",
        "12 minutes of pure emotion.",
        "That mellotron intro is unforgettable.",
        "The climax is earth-shattering.",
        "King Crimson's magnum opus.",
        "Progressive rock at its peak.",
        "I cry every single time.",
        "Nothing else comes close.",
        "The saxophone section is haunting.",
        "A journey from beauty to chaos.",
    ],
    'Reckoner': [
        "Thom Yorke's voice is angelic here.",
        "The percussion is so unique.",
        "Beautiful and haunting.",
        "In Rainbows' crown jewel.",
        "Makes me feel things I can't describe.",
        "The strings at the end are perfect.",
        "Radiohead at their most tender.",
        "Ethereal and gorgeous.",
        "One of the best songs of the 2000s.",
        "Pure sonic beauty.",
    ],
}

# ─── Usernames ─────────────────────────────────────────────────────

FIRST_NAMES = [
    'alex', 'jordan', 'casey', 'riley', 'morgan', 'taylor', 'quinn', 'avery',
    'charlie', 'sam', 'drew', 'jamie', 'robin', 'jesse', 'sky', 'sage',
    'blake', 'parker', 'logan', 'reese', 'hayden', 'emerson', 'finley', 'rowan',
    'ellis', 'river', 'kai', 'nico', 'jules', 'remy', 'arlo', 'ezra',
    'nova', 'wren', 'ivy', 'zara', 'mika', 'luca', 'felix', 'oscar',
    'leo', 'milo', 'theo', 'hugo', 'otto', 'nina', 'luna', 'maya',
    'zoe', 'aria', 'elias', 'stella', 'cleo', 'ruby', 'jade', 'opal',
    'miles', 'dean', 'cole', 'reed', 'dale', 'noel', 'evan', 'seth',
    'mark', 'joel', 'paul', 'neil', 'ross', 'sean', 'kurt', 'glen',
    'hank', 'wade', 'troy', 'kent', 'lars', 'beau', 'cruz', 'dane',
    'erik', 'finn', 'grey', 'hart', 'jack', 'kane', 'liam', 'marc',
    'nate', 'owen', 'pete', 'raul', 'stan', 'tony', 'vick', 'walt',
    'yuri', 'zack', 'adam', 'brad',
]

# ─── Step 1: Fetch song data from MusicBrainz API ─────────────────

print("Fetching song data from MusicBrainz API...")
song_objects = []

for release_info in RELEASES:
    release_id = release_info['release_id']
    target_song = release_info['target_song']

    print(f"  Fetching release {release_id}...")

    # Fetch release with recordings and artist credits and release groups
    response = http_requests.get(
        f'{MB_BASE}/release/{release_id}',
        params={'fmt': 'json', 'inc': 'recordings+artist-credits+release-groups'},
        headers=MB_HEADERS,
    )
    time.sleep(1.1)  # Respect rate limit

    if response.status_code != 200:
        print(f"  ERROR: Could not fetch release {release_id}")
        continue

    release_data = response.json()

    # Get artist info
    artist_credit = release_data.get('artist-credit', [{}])
    artist_name = artist_credit[0].get('name', 'Unknown')
    artist_id = artist_credit[0].get('artist', {}).get('id', '')

    # Get album info
    album_title = release_data.get('title', 'Unknown')
    release_group = release_data.get('release-group', {})
    release_group_id = release_group.get('id', '')
    release_date = release_data.get('date', '')

    # Find the target song in the tracklist
    found = False
    for medium in release_data.get('media', []):
        for track in medium.get('tracks', []):
            recording = track.get('recording', {})
            if recording.get('title', '').lower() == target_song.lower():
                recording_id = recording.get('id', '')
                track_number = track.get('position', 0)
                duration = recording.get('length', 0)

                # Create or get Artist
                artist, _ = Artist.objects.get_or_create(
                    musicbrainz_id=artist_id,
                    defaults={'name': artist_name},
                )

                # Create or get Album
                album, _ = Album.objects.get_or_create(
                    musicbrainz_id=release_group_id,
                    defaults={
                        'title': album_title,
                        'artist': artist,
                        'release_date': release_date if release_date else None,
                    },
                )

                # Create or get Song
                song, _ = Song.objects.get_or_create(
                    musicbrainz_id=recording_id,
                    defaults={
                        'title': target_song,
                        'album': album,
                        'track_number': track_number,
                        'duration_ms': duration or 0,
                    },
                )

                song_objects.append(song)
                print(f"  OK {target_song} - {artist_name} (recording: {recording_id})")
                found = True
                break
        if found:
            break

    if not found:
        print(f"  ERROR: Could not find '{target_song}' in release {release_id}")

if len(song_objects) != 3:
    print(f"\nERROR: Only found {len(song_objects)} of 4 songs. Aborting.")
    sys.exit(1)

# ─── Step 2: Create 100 users and ratings ──────────────────────────

print(f"\nCreating 100 users and ratings...")
random.seed(42)

created_count = 0
for i, username in enumerate(FIRST_NAMES[:100]):
    full_username = f"{username}_{random.randint(100, 999)}"

    if User.objects.filter(username=full_username).exists():
        continue

    user = User.objects.create_user(
        username=full_username,
        password='testpass123',
    )

    country = random.choice(COUNTRY_POOL)
    Profile.objects.create(
        user=user,
        display_name=username.capitalize(),
        country=country,
    )

    for song in song_objects:
        score = Decimal(str(round(random.uniform(8.0, 10.0), 1)))

        review_text = ''
        if random.random() < 0.4:
            song_reviews = REVIEWS.get(song.title, [])
            if song_reviews:
                review_text = random.choice(song_reviews)

        Rating.objects.create(
            user=user,
            song=song,
            score=score,
            review_text=review_text,
        )

    created_count += 1
    if created_count % 10 == 0:
        print(f"  Created {created_count} users...")

print(f"\nDone! Created {created_count} users with {created_count * 4} ratings.")
print(f"Songs rated: {', '.join(s.title for s in song_objects)}")