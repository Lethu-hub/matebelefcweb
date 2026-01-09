import csv
from django.core.management.base import BaseCommand
from adminpanel.models import MatchEvent, Match, Player

class Command(BaseCommand):
    help = 'Import match events from a CSV file (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to match events CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    match = Match.objects.get(match_id=row.get('Match_ID'))
                    player = Player.objects.get(player_id=row.get('Player_ID'))

                    MatchEvent.objects.update_or_create(
                        match=match,
                        player=player,
                        event_type=row.get('Event_Type', ''),
                        minute=int(row.get('Minute', 0)) if row.get('Minute') else None,
                        season=row.get('Season', ''),
                        defaults={'description': ''}
                    )
                except Match.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Match {row.get('Match_ID')} not found"))
                except Player.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Player {row.get('Player_ID')} not found"))

        self.stdout.write(self.style.SUCCESS('Match events imported successfully (idempotent)!'))
