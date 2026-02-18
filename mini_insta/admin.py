# File: admin.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/18/2026
# Description: Registers mini_insta models with the Django admin site.
from django.contrib import admin
from .models import Profile

# Register your models here.
admin.site.register(Profile)