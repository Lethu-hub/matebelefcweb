# adminpanel/models.py
import uuid
from django.db import models

class Player(models.Model):
    player_id = models.CharField(max_length=20, unique=True)  # was UUIDField
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    position = models.CharField(max_length=50, blank=True)
    height_cm = models.IntegerField(null=True, blank=True)

class Match(models.Model):
    match_id = models.CharField(max_length=20, unique=True)  # was UUIDField
    match_date = models.DateField(null=True, blank=True)
    season = models.CharField(max_length=10, blank=True)

class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    minute = models.IntegerField(null=True, blank=True)

