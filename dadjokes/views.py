# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: View functions for the dadjokes app. Includes template-based
# views for rendering HTML pages, and REST API views that return JSON
# responses for Joke and Picture data. The API supports GET and POST methods.

from django.shortcuts import render, get_object_or_404
from .models import Joke, Picture
from .serializers import JokeSerializer, PictureSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random

# ─── Template-based Views ───────────────────────────────────

def random_joke_and_picture(request):
    """Show one random Joke and one random Picture (for '' and 'random' URLs)."""
    jokes = Joke.objects.all()
    pictures = Picture.objects.all()
    context = {
        'joke': random.choice(list(jokes)) if jokes else None,
        'picture': random.choice(list(pictures)) if pictures else None,
    }
    return render(request, 'dadjokes/random.html', context)

def all_jokes(request):
    """Show all Jokes."""
    context = {'jokes': Joke.objects.all().order_by('-created')}
    return render(request, 'dadjokes/jokes.html', context)

def one_joke(request, pk):
    """Show one Joke by primary key."""
    context = {'joke': get_object_or_404(Joke, pk=pk)}
    return render(request, 'dadjokes/joke_detail.html', context)

def all_pictures(request):
    """Show all Pictures."""
    context = {'pictures': Picture.objects.all().order_by('-created')}
    return render(request, 'dadjokes/pictures.html', context)

def one_picture(request, pk):
    """Show one Picture by primary key."""
    context = {'picture': get_object_or_404(Picture, pk=pk)}
    return render(request, 'dadjokes/picture_detail.html', context)

# ─── REST API Views ─────────────────────────────────────────

@api_view(['GET'])
def api_random_joke(request):
    """Return a JSON representation of one random Joke."""
    jokes = Joke.objects.all()
    if not jokes:
        return Response({'error': 'No jokes found'}, status=404)
    joke = random.choice(list(jokes))
    serializer = JokeSerializer(joke)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def api_all_jokes(request):
    """GET: return all Jokes as JSON. POST: create a new Joke."""
    if request.method == 'GET':
        jokes = Joke.objects.all().order_by('-created')
        serializer = JokeSerializer(jokes, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = JokeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_one_joke(request, pk):
    """Return one Joke by primary key as JSON."""
    joke = get_object_or_404(Joke, pk=pk)
    serializer = JokeSerializer(joke)
    return Response(serializer.data)

@api_view(['GET'])
def api_all_pictures(request):
    """Return all Pictures as JSON."""
    pictures = Picture.objects.all().order_by('-created')
    serializer = PictureSerializer(pictures, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_one_picture(request, pk):
    """Return one Picture by primary key as JSON."""
    picture = get_object_or_404(Picture, pk=pk)
    serializer = PictureSerializer(picture)
    return Response(serializer.data)

@api_view(['GET'])
def api_random_picture(request):
    """Return a JSON representation of one random Picture."""
    pictures = Picture.objects.all()
    if not pictures:
        return Response({'error': 'No pictures found'}, status=404)
    picture = random.choice(list(pictures))
    serializer = PictureSerializer(picture)
    return Response(serializer.data)