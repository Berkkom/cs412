# File: forms.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/29/2026
# Description: Django forms for the music rating application.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    '''Custom registration form that includes display name and country.'''
    display_name = forms.CharField(
        max_length=100,
        required=True,
        help_text='This is how your name will appear on your profile.',
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        help_text='Your country (e.g. United States, Turkey, France).',
    )

    class Meta:
        model = User
        fields = ('username', 'display_name', 'country', 'password1', 'password2')