import csv
from django.core.management.base import BaseCommand
from adminpanel.models import MatchEvent, Match, Player
import os
import csv as _csv
import json

class Command(BaseCommand):
    help = 'Import match events from a CSV file (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='match_events.csv')
        parser.add_argument('--use-mapping', action='store_true', help='Use adminpanel/mappings/*_map.csv to remap CSV ids to new generated ids')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        use_mapping = kwargs.get('use_mapping')
        players_map = {}
        matches_map = {}
        if use_mapping:
            pmap = os.path.join('adminpanel', 'mappings', 'players_map.csv')
            mmap = os.path.join('adminpanel', 'mappings', 'matches_map.csv')
            if os.path.exists(pmap):
                with open(pmap, newline='', encoding='utf-8') as pf:
                    r = _csv.DictReader(pf)
                    for row in r:
                        players_map[row['old_id']] = row['new_id']
            if os.path.exists(mmap):
                with open(mmap, newline='', encoding='utf-8') as mf:
                    r = _csv.DictReader(mf)
                    for row in r:
                        matches_map[row['old_id']] = row['new_id']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # remap ids if mapping provided
                csv_mid = row.get('Match_ID')
                csv_pid = row.get('Player_ID')
                mid = matches_map.get(csv_mid, csv_mid)
                pid = players_map.get(csv_pid, csv_pid)
                try:
                    match = Match.objects.get(match_id=mid)
                    player = Player.objects.get(player_id=pid)

                    # Use only match and player as the lookup keys
                    MatchEvent.objects.update_or_create(
                        match=match,
                        player=player,
                        defaults={
                            'event_type': row.get('Event_Type', ''),
                            'minute': int(row.get('Minute', 0)) if row.get('Minute') else None,
                            'season': row.get('Season', ''),
                            'description': row.get('Description', '')  # optional, will be blank if not in CSV
                        }
                    )
                except Match.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Match {mid} not found"))
                except Player.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Player {pid} not found"))

        self.stdout.write(self.style.SUCCESS('Match events imported successfully (idempotent)!'))
