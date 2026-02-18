# File: models.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 02/17/2026
# Description: Contains the models for the mini_insta app.
from django.db import models

# Create your models here.
class Profile(models.Model):

    username = models.TextField(blank=False)
    display_name = models.TextField(blank=False)
    profile_image_url = models.TextField(blank=False)
    bio_text = models.TextField(blank=False)
    join_date = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.username} created {self.join_date}'