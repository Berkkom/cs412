# File: views.py
# Author: Berk Komurcuoglu (berkkom@bu.edu), 3/19/2026
# Description: Views for the voter_analytics application, including
# the voter list, voter detail page, and graph display page.

from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from .models import Voter

import plotly.graph_objects as go
from plotly.offline import plot


class VoterFilterMixin:
    """Provide shared filtering logic and filter-form context data."""

    def get_filtered_queryset(self):
        """Return the queryset after applying any selected voter filters."""
        qs = Voter.objects.all().order_by("last_name", "first_name")

        party = self.request.GET.get("party")
        min_year = self.request.GET.get("min_year")
        max_year = self.request.GET.get("max_year")
        voter_score = self.request.GET.get("voter_score")

        v20state = self.request.GET.get("v20state")
        v21town = self.request.GET.get("v21town")
        v21primary = self.request.GET.get("v21primary")
        v22general = self.request.GET.get("v22general")
        v23town = self.request.GET.get("v23town")

        if party:
            qs = qs.filter(party_affiliation=party)

        if min_year:
            qs = qs.filter(date_of_birth__year__gte=min_year)

        if max_year:
            qs = qs.filter(date_of_birth__year__lte=max_year)

        if voter_score:
            qs = qs.filter(voter_score=voter_score)

        if v20state:
            qs = qs.filter(v20state=True)

        if v21town:
            qs = qs.filter(v21town=True)

        if v21primary:
            qs = qs.filter(v21primary=True)

        if v22general:
            qs = qs.filter(v22general=True)

        if v23town:
            qs = qs.filter(v23town=True)

        return qs

    def get_filter_context(self):
        """Return context data needed to display and preserve filter values."""
        dob_dates = Voter.objects.exclude(date_of_birth__isnull=True).dates(
            "date_of_birth", "year"
        )
        years = [d.year for d in dob_dates]

        parties = (
            Voter.objects.order_by("party_affiliation")
            .values_list("party_affiliation", flat=True)
            .distinct()
        )

        # Preserve all current filters when moving between pagination links.
        current_filters = self.request.GET.copy()
        if "page" in current_filters:
            current_filters.pop("page")

        return {
            "parties": parties,
            "years": years,
            "scores": [0, 1, 2, 3, 4, 5],
            "selected_party": self.request.GET.get("party", ""),
            "selected_min_year": self.request.GET.get("min_year", ""),
            "selected_max_year": self.request.GET.get("max_year", ""),
            "selected_score": self.request.GET.get("voter_score", ""),
            "selected_v20state": self.request.GET.get("v20state", ""),
            "selected_v21town": self.request.GET.get("v21town", ""),
            "selected_v21primary": self.request.GET.get("v21primary", ""),
            "selected_v22general": self.request.GET.get("v22general", ""),
            "selected_v23town": self.request.GET.get("v23town", ""),
            "current_filters": current_filters.urlencode(),
        }


class VoterListView(VoterFilterMixin, ListView):
    """Display a paginated list of voters with optional filtering."""

    model = Voter
    template_name = "voter_analytics/voter_list.html"
    context_object_name = "voters"
    paginate_by = 100

    def get_queryset(self):
        """Return the filtered queryset for the voter list page."""
        return self.get_filtered_queryset()

    def get_context_data(self, **kwargs):
        """Add filter-related values to the template context."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_filter_context())
        return context


class VoterDetailView(DetailView):
    """Display detailed information for a single voter."""

    model = Voter
    template_name = "voter_analytics/voter_detail.html"
    context_object_name = "voter"


class GraphListView(VoterFilterMixin, ListView):
    """Display graphs summarizing voter data for the filtered queryset."""

    model = Voter
    template_name = "voter_analytics/graphs.html"
    context_object_name = "voters"

    def get_queryset(self):
        """Return the filtered queryset used to generate the graphs."""
        return self.get_filtered_queryset()

    def get_context_data(self, **kwargs):
        """Add plotly graph divs and filter values to the template context."""
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        # Graph 1: distribution of voters by year of birth.
        birth_data = (
            qs.exclude(date_of_birth__isnull=True)
            .values("date_of_birth__year")
            .annotate(count=Count("id"))
            .order_by("date_of_birth__year")
        )

        birth_years = [row["date_of_birth__year"] for row in birth_data]
        birth_counts = [row["count"] for row in birth_data]

        fig_birth = go.Figure(data=[go.Bar(x=birth_years, y=birth_counts)])
        fig_birth.update_layout(
            title="Distribution of Voters by Year of Birth",
            xaxis_title="Birth Year",
            yaxis_title="Number of Voters",
            margin=dict(l=40, r=20, t=60, b=40),
        )
        context["birth_graph"] = plot(fig_birth, output_type="div")

        # Graph 2: distribution of voters by party affiliation.
        party_data = (
            qs.values("party_affiliation")
            .annotate(count=Count("id"))
            .order_by("party_affiliation")
        )

        party_labels = [
            row["party_affiliation"].strip() if row["party_affiliation"] else "Unknown"
            for row in party_data
        ]
        party_counts = [row["count"] for row in party_data]

        fig_party = go.Figure(data=[go.Pie(labels=party_labels, values=party_counts)])
        fig_party.update_layout(title="Distribution of Voters by Party Affiliation")
        context["party_graph"] = plot(fig_party, output_type="div")

        # Graph 3: number of voters who participated in each election.
        election_counts = qs.aggregate(
            count_v20state=Count("id", filter=Q(v20state=True)),
            count_v21town=Count("id", filter=Q(v21town=True)),
            count_v21primary=Count("id", filter=Q(v21primary=True)),
            count_v22general=Count("id", filter=Q(v22general=True)),
            count_v23town=Count("id", filter=Q(v23town=True)),
        )

        election_labels = [
            "2020 State",
            "2021 Town",
            "2021 Primary",
            "2022 General",
            "2023 Town",
        ]
        election_values = [
            election_counts["count_v20state"],
            election_counts["count_v21town"],
            election_counts["count_v21primary"],
            election_counts["count_v22general"],
            election_counts["count_v23town"],
        ]

        fig_elections = go.Figure(data=[go.Bar(x=election_labels, y=election_values)])
        fig_elections.update_layout(
            title="Voter Participation by Election",
            xaxis_title="Election",
            yaxis_title="Number of Voters",
        )
        context["election_graph"] = plot(fig_elections, output_type="div")

        context.update(self.get_filter_context())
        return context