from django.db import models
from django.contrib.auth.models import User


class PoliceStation(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class StationProfile(models.Model):
    """
    Connects Django User -> PoliceStation
    Only these users can login as 'Station Admin'
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    station = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ({self.station.name})"


class MissingChild(models.Model):
    station = models.ForeignKey(PoliceStation, on_delete=models.CASCADE, related_name="cases")

    child_name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    last_seen_location = models.CharField(max_length=200)
    details = models.TextField(blank=True)

    image = models.ImageField(upload_to="missing_children/")
    embedding = models.BinaryField()

    status = models.CharField(max_length=20, default="missing")  # missing/found
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child_name} - {self.station.name}"


class Report(models.Model):
    """
    Public user upload (no login).
    If matched -> station + matched_case filled.
    """
    reporter_name = models.CharField(max_length=100)
    reporter_phone = models.CharField(max_length=20)
    found_location = models.CharField(max_length=250)
    notes = models.TextField(blank=True)

    image = models.ImageField(upload_to="reports/")
    created_at = models.DateTimeField(auto_now_add=True)

    # match results (nullable if no match)
    matched_case = models.ForeignKey(MissingChild, null=True, blank=True, on_delete=models.SET_NULL)
    matched_station = models.ForeignKey(PoliceStation, null=True, blank=True, on_delete=models.SET_NULL)
    distance = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, default="unmatched")  # unmatched/matched
    is_seen_by_station = models.BooleanField(default=False)        # notification badge

    def __str__(self):
        return f"Report by {self.reporter_name} ({self.status})"
