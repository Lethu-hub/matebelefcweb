# adminpanel/models.py
import uuid
from django.db import models

class Player(models.Model):
    player_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    jersey_number = models.PositiveIntegerField(blank=True, null=True)
    height_cm = models.PositiveIntegerField(blank=True, null=True)
    weight_kg = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.surname}"

class Match(models.Model):
    match_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match_date = models.DateField()
    opponent = models.CharField(max_length=100)
    venue = models.CharField(max_length=100, blank=True, null=True)
    result = models.CharField(max_length=10, blank=True, null=True)
    score_mfc = models.PositiveIntegerField(blank=True, null=True)
    score_opponent = models.PositiveIntegerField(blank=True, null=True)
    season = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.match_date} vs {self.opponent}"

class MatchEvent(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    minute = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    season = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.event_type} - {self.player}"
