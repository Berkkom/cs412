# File: apps.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: App configuration for the dadjokes Django application.

from django.apps import AppConfig

class DadjokesConfig(AppConfig):
    """Configuration class for the dadjokes application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dadjokes'