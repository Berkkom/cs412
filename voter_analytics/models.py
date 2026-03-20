# File: models.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 3/19/2026
# Description: Model definitions and data-loading utilities for the
# voter_analytics application.

from django.db import models
from django.conf import settings
from pathlib import Path
import csv
from datetime import datetime
from urllib.parse import quote_plus


class Voter(models.Model):
    """Represent a registered voter in Newton, Massachusetts."""

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)

    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=200)
    apartment_number = models.CharField(max_length=20, blank=True)

    zip_code = models.CharField(max_length=10)

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_registration = models.DateField(null=True, blank=True)

    party_affiliation = models.CharField(max_length=2, blank=True)
    precinct_number = models.CharField(max_length=10, blank=True, null=True)

    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)

    voter_score = models.IntegerField(default=0)

    def __str__(self):
        """Return a readable string representation of this voter."""
        return f"{self.first_name} {self.last_name} ({self.street_number} {self.street_name})"

    def street_address(self):
        """Return the voter's street address, including apartment if present."""
        if self.apartment_number:
            return f"{self.street_number} {self.street_name}, Apt {self.apartment_number}"
        return f"{self.street_number} {self.street_name}"

    def full_address(self):
        """Return the voter's complete mailing address in Newton, MA."""
        return f"{self.street_address()}, Newton, MA {self.zip_code}"

    def google_maps_url(self):
        """Return a Google Maps search URL for the voter's address."""
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(self.full_address())}"


def parse_date(date_str):
    """Convert a CSV date string into a Python date object, if possible."""
    if not date_str or date_str.strip() == "":
        return None

    date_str = date_str.strip()

    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def parse_bool(value):
    """Convert a CSV election-participation value into True or False."""
    if not value:
        return False

    value = value.strip().upper()
    return value in {"TRUE", "T", "Y", "YES", "1"}


def load_data():
    """Load voter records from newton_voters.csv into the database."""
    csv_file = Path(settings.BASE_DIR) / "newton_voters.csv"

    if not csv_file.exists():
        print(f"CSV file not found: {csv_file}")
        return

    # Delete existing records so repeated imports do not create duplicates.
    Voter.objects.all().delete()

    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        voters_to_create = []

        for row in reader:
            voter = Voter(
                last_name=row["Last Name"].strip(),
                first_name=row["First Name"].strip(),
                street_number=row["Residential Address - Street Number"].strip(),
                street_name=row["Residential Address - Street Name"].strip(),
                apartment_number=row["Residential Address - Apartment Number"].strip(),
                zip_code=row["Residential Address - Zip Code"].strip(),
                date_of_birth=parse_date(row["Date of Birth"]),
                date_of_registration=parse_date(row["Date of Registration"]),
                party_affiliation=row["Party Affiliation"].strip(),
                precinct_number=row["Precinct Number"].strip(),
                v20state=parse_bool(row["v20state"]),
                v21town=parse_bool(row["v21town"]),
                v21primary=parse_bool(row["v21primary"]),
                v22general=parse_bool(row["v22general"]),
                v23town=parse_bool(row["v23town"]),
                voter_score=int(row["voter_score"]) if row["voter_score"].strip() else 0,
            )
            voters_to_create.append(voter)

        Voter.objects.bulk_create(voters_to_create)

    print(f"Loaded {Voter.objects.count()} voters.")