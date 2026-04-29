# File: music_filters.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 4/29/2026
# Description: Custom template filters for the music rating application.

from django import template

register = template.Library()

@register.filter
def ms_to_duration(ms):
    '''Convert milliseconds to min:sec format (e.g. 470000 -> "7:50").'''
    if not ms:
        return "0:00"
    total_seconds = int(ms) // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"