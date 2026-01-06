# adminpanel/models.py
import uuid
from django.db import models


class Player(models.Model):
    player_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=50, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    height_cm = models.IntegerField(null=True, blank=True)
    weight_kg = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.surname}"


class Match(models.Model):
    match_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    match_date = models.DateField()
    opponent = models.CharField(max_length=100)
    venue = models.CharField(max_length=100, blank=True)
    result = models.CharField(max_length=20, blank=True)
    score_mfc = models.IntegerField(null=True, blank=True)
    score_opponent = models.IntegerField(null=True, blank=True)
    season = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"MFC vs {self.opponent} ({self.match_date})"


class MatchEvent(models.Model):
    event_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="events"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="events"
    )
    event_type = models.CharField(max_length=50)
    minute = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    season = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.event_type} - {self.player}"
