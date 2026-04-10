# File: serializers.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/10/2026
# Description: REST API serializers for mini_insta models.

from rest_framework import serializers
from .models import Profile, Post, Photo, Like, Comment, Follow


class PhotoSerializer(serializers.ModelSerializer):
    """Serialize a Photo, returning an absolute image URL."""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "image_url", "timestamp"]

    def get_image_url(self, obj):
        """Return the full URL for the photo, preferring image_url over image_file."""
        if obj.image_url:
            return obj.image_url
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return ""


class PostSerializer(serializers.ModelSerializer):
    """Serialize a Post with nested photos and like count."""
    photos = PhotoSerializer(source="photo_set", many=True, read_only=True)
    num_likes = serializers.SerializerMethodField()
    profile_username = serializers.CharField(source="profile.username", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "profile", "profile_username", "caption", "timestamp", "photos", "num_likes"]
        read_only_fields = ["profile", "timestamp"]

    def get_num_likes(self, obj):
        """Return the total number of likes on this post."""
        return obj.get_num_likes()


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize a Profile with follower and following counts."""
    num_followers = serializers.SerializerMethodField()
    num_following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id", "username", "display_name", "profile_image_url",
            "bio_text", "join_date", "num_followers", "num_following",
        ]

    def get_num_followers(self, obj):
        """Return the number of followers for this profile."""
        return obj.get_num_followers()

    def get_num_following(self, obj):
        """Return the number of profiles this profile follows."""
        return obj.get_num_following()