from django.db import models
from django.conf import settings
from pathlib import Path
import csv
from datetime import datetime


class Voter(models.Model):
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
        return f"{self.first_name} {self.last_name} ({self.street_number} {self.street_name})"


def parse_date(date_str):
    """
    Convert a string date from the CSV into a Python date object.
    Tries a few common formats.
    """
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
    """
    Convert CSV election participation values into True/False.
    Handles values like TRUE, T, Y, YES, 1.
    """
    if not value:
        return False

    value = value.strip().upper()
    return value in {"TRUE", "T", "Y", "YES", "1"}


def load_data():
    """
    Load voter data from newton_voters.csv into the database.
    Assumes the CSV file is located in the Django project base directory.
    """

    csv_file = Path(settings.BASE_DIR) / "newton_voters.csv"

    if not csv_file.exists():
        print(f"CSV file not found: {csv_file}")
        return

    # Delete old records so repeated imports do not create duplicates
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