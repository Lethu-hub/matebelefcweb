import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from adminpanel.models import Match

class Command(BaseCommand):
    help = 'Import matches from a CSV file (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to matches CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                match_date = None
                if row.get('Match_Date'):
                    try:
                        match_date = datetime.strptime(row.get('Match_Date'), '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Invalid date {row.get('Match_Date')}"))

                Match.objects.update_or_create(
                    match_id=row.get('Match_ID'),
                    defaults={
                        'match_date': match_date,
                        'opponent': row.get('Opponent', ''),
                        'venue': row.get('Venue', ''),
                        'result': row.get('Result', ''),
                        'score_mfc': int(row.get('Score_MFC', 0)) if row.get('Score_MFC') else None,
                        'score_opponent': int(row.get('Score_Opponent', 0)) if row.get('Score_Opponent') else None,
                        'season': row.get('Season', '')
                    }
                )
        self.stdout.write(self.style.SUCCESS('Matches imported successfully (idempotent)!'))
