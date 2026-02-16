# File: urls.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/15/2026
# Description: URL patterns for the restaurant app, mapping routes for the
# main page, order page, and confirmation page to their view functions.

from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = "restaurant"

urlpatterns = [
    # Displays general restaurant information (name, location, hours, photos).
    path("main/", views.main, name="main"),

    # Displays the order form. 
    # The view randomly selects a daily special and
    # passes it to the template via the context dictionary.
    path("order/", views.order, name="order"),

    # Handles the POST submission of the order form. The view reads the form
    # fields, determines which menu items were checked, computes the total,
    # and displays a confirmation page with a ready time 30–60 minutes from now.
    path("confirmation/", views.confirmation, name="confirmation"),
]