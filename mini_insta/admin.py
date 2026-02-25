# File: admin.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/20/2026
# Description: Registers mini_insta models with the Django admin site.
from django.contrib import admin
from .models import Profile, Photo, Post, Follow, Comment, Like

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)