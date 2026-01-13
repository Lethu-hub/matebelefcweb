# adminpanel/models.py
from django.db import models
from django.utils import timezone
import re


def _next_player_id():
    # Find numeric suffix among existing P### ids
    qs = Player.objects.all().values_list('player_id', flat=True)
    maxn = 0
    for pid in qs:
        m = re.match(r'^P(\d+)$', pid or '')
        if m:
            n = int(m.group(1))
            if n > maxn:
                maxn = n
    return f'P{maxn+1:03d}'


def _next_match_id(match_date=None):
    year = (match_date.year if match_date else timezone.now().year)
    prefix = f'M{year}_'
    qs = Match.objects.filter(match_id__startswith=prefix).values_list('match_id', flat=True)
    maxn = 0
    for mid in qs:
        m = re.match(r'^M\d+_(\d+)$', mid or '')
        if m:
            n = int(m.group(1))
            if n > maxn:
                maxn = n
    return f'{prefix}{maxn+1:03d}'


class Player(models.Model):
    # Use formatted string like P001 as primary key
    player_id = models.CharField(primary_key=True, max_length=10, editable=False)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    position = models.CharField(max_length=50, blank=True)
    height_cm = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.player_id:
            self.player_id = _next_player_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.surname}"


class Match(models.Model):
    # Use formatted string like M2023_001 as primary key
    match_id = models.CharField(primary_key=True, max_length=20, editable=False)
    match_date = models.DateField(null=True, blank=True)
    season = models.CharField(max_length=10, blank=True)
    # Allow assigning many players to a match (roster)
    players = models.ManyToManyField('Player', blank=True, related_name='matches')

    def save(self, *args, **kwargs):
        if not self.match_id:
            self.match_id = _next_match_id(self.match_date)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.match_date} ({self.match_id})"

class MatchEvent(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    minute = models.IntegerField(null=True, blank=True)
    season = models.CharField(max_length=20, blank=True, null=True)         # new field for season
    description = models.TextField(blank=True, null=True)                    # new field for any extra notes

    def __str__(self):
        return f"{self.event_type} by {self.player} in match {self.match}"