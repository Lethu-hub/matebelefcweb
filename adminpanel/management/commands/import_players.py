import csv
from django.core.management.base import BaseCommand
from adminpanel.models import Player

class Command(BaseCommand):
    help = 'Import players from a CSV file (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to players CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Player.objects.update_or_create(
                    player_id=row.get('Player_ID'),
                    defaults={
                        'first_name': row.get('First_Name', ''),
                        'surname': row.get('Surname', ''),
                        'position': row.get('Position', ''),
                        'height_cm': int(row.get('Height', 0)) if row.get('Height') else None,
                        'weight_kg': None,  # optional, leave blank
                        'date_of_birth': None  # optional, leave blank
                    }
                )
        self.stdout.write(self.style.SUCCESS('Players imported successfully (idempotent)!'))
