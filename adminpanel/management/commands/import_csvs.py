import csv
from django.core.management.base import BaseCommand
from adminpanel.models import Player, Match, MatchEvent
from datetime import datetime

class Command(BaseCommand):
    help = 'Import players, matches, and match events from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--players', type=str, help='Path to players CSV')
        parser.add_argument('--matches', type=str, help='Path to matches CSV')
        parser.add_argument('--events', type=str, help='Path to match events CSV')

    def handle(self, *args, **options):
        players_file = options['players']
        matches_file = options['matches']
        events_file = options['events']

        if players_file:
            self.stdout.write('Importing Players...')
            with open(players_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    Player.objects.update_or_create(
                        player_id=row['player_id'],
                        defaults={
                            'first_name': row['first_name'],
                            'surname': row['surname'],
                            'date_of_birth': datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date(),
                            'nationality': row['nationality'],
                            'position': row['position'],
                            'jersey_number': row['jersey_number'],
                            'height_cm': row['height_cm'],
                            'weight_kg': row['weight_kg'],
                        }
                    )

        if matches_file:
            self.stdout.write('Importing Matches...')
            with open(matches_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    Match.objects.update_or_create(
                        match_id=row['match_id'],
                        defaults={
                            'match_date': datetime.strptime(row['match_date'], '%Y-%m-%d').date(),
                            'opponent': row['opponent'],
                            'venue': row['venue'],
                            'result': row['result'],
                            'score_mfc': row['score_mfc'],
                            'score_opponent': row['score_opponent'],
                            'season': row['season'],
                        }
                    )

        if events_file:
            self.stdout.write('Importing Match Events...')
            with open(events_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    MatchEvent.objects.update_or_create(
                        event_id=row['event_id'],
                        defaults={
                            'match_id_id': row['match_id'],  # ForeignKey
                            'player_id_id': row['player_id'],  # ForeignKey
                            'event_type': row['event_type'],
                            'minute': row['minute'],
                            'description': row['description'],
                            'season': row['season'],
                        }
                    )

        self.stdout.write(self.style.SUCCESS('CSV Import Complete!'))
