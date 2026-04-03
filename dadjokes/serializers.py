# File: serializers.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: Django REST Framework serializers for the Joke and Picture
# models. Converts model instances to/from JSON representations.

from rest_framework import serializers
from .models import Joke, Picture

class JokeSerializer(serializers.ModelSerializer):
    """Serializer for the Joke model. Converts Joke instances to/from JSON."""
    class Meta:
        model = Joke
        fields = ['id', 'text', 'contributor', 'created']

class PictureSerializer(serializers.ModelSerializer):
    """Serializer for the Picture model. Converts Picture instances to/from JSON."""
    class Meta:
        model = Picture
        fields = ['id', 'image_url', 'contributor', 'created']