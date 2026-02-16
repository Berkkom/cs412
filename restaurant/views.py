# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 2/15/2026
# Description: View functions for the restaurant app, including the main
# page, the order form page (with a randomly selected daily special), and
# the confirmation page that processes submitted form data.
 
from django.shortcuts import render, redirect
import random
import time
from datetime import datetime

# -----------------------------
# Menu data (simple dictionaries)
# -----------------------------
# MENU keys MUST match the checkbox "name" attributes in order.html.
# Each item has a display name and a price.
MENU = {
    "carbonara": {"name": "Carbonara", "price": 12},
    "cacio": {"name": "Cacio e pepe", "price": 10},
    "florentine": {"name": "Florentine Steak", "price": 65},
    "risotto": {"name": "Risotto alla Milanese", "price": 16}
}

# Options / extras for Florentine Steak.
# These are optional add-ons and only count if florentine is selected.
FLORENTINE_EXTRAS = {
    "asparagus": {"label": "Asparagus", "price": 7},
    "fries": {"label": "Truffle Fries", "price": 10},
    "mashed": {"label": "Mashed Potatoes", "price": 12}
}

# Daily specials list.
DAILY_SPECIALS = [
    {
        "name": "Ossobuco", 
        "desc": "Veal shank braised with in vegetables, white wine, and broth, served with Risotto alla Milanese", 
        "price": 50
    },
    {
        "name": "Pappardelle alla Bolognese", 
        "desc": "Pappardelle pasta served with slow-cooked meat ragù", 
        "price": 17
    },
    {
        "name": "Ravioli al Tartufo", 
        "desc": "Fresh egg pasta filled with ricotta served with black truffle-infused butter sauce", 
        "price": 16
    },
]
def main(request):
    """Display the restaurant main page (name, location, hours, photos)."""
    return render(request, "restaurant/main.html")

def order(request):
    """Display the order form and include a randomly selected daily special."""
    special_index = random.randrange(len(DAILY_SPECIALS))
    context = {
        "menu": MENU,
        "florentine_extras": FLORENTINE_EXTRAS,
        "daily_special": DAILY_SPECIALS[special_index],
        "special_index": special_index,
    }
    return render(request, "restaurant/order.html", context)

def confirmation(request):
    """Process the submitted order form and display an order confirmation."""
    if request.method != "POST":
        return redirect("restaurant:order")  
    ordered_items = []
    total = 0.0

    # customer info
    customer_name = request.POST.get("customer_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip()
    instructions = request.POST.get("instructions", "").strip()

    # main menu items (robust: checks presence, not value)
    for key, item in MENU.items():
        if key in request.POST:
            ordered_items.append({"name": item["name"], "price": float(item["price"])})
            total += float(item["price"])

    # Florentine extras only if Florentine was selected
    if "florentine" in request.POST:
        extras_total = 0.0
        chosen_extras = []

        for extra_key, extra in FLORENTINE_EXTRAS.items():
            if extra_key in request.POST:
                chosen_extras.append(extra["label"])
                extras_total += float(extra["price"])

        if chosen_extras:
            ordered_items.append({
                "name": "Florentine Sides",
                "price": extras_total,
                "details": ", ".join(chosen_extras),
            })
            total += extras_total

    # Daily special
    if "daily_special" in request.POST:
        try:
            idx = int(request.POST.get("special_index", "0"))
            special = DAILY_SPECIALS[idx]
            ordered_items.append({
                "name": f"Daily Special: {special['name']}",
                "price": float(special["price"]),
                "details": special.get("desc", ""),
            })
            total += float(special["price"])
        except (ValueError, IndexError):
            pass

    # ready time 30–60 minutes from now
    minutes = random.randint(30, 60)
    ready_epoch = time.time() + minutes * 60

    # format in LOCAL time
    ready_time_str = time.strftime("%A, %B %d at %I:%M %p", time.localtime(ready_epoch))
    
    context = {
        "customer_name": customer_name,
        "phone": phone,
        "email": email,
        "instructions": instructions,
        "ordered_items": ordered_items,
        "total": f"{total:.2f}",
        "ready_time": ready_time_str,
    }
    return render(request, "restaurant/confirmation.html", context)

