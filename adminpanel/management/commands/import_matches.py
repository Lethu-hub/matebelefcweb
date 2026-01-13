import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from adminpanel.models import Match
import os
import csv as _csv

class Command(BaseCommand):
    help = 'Import matches from a CSV file (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='matches.csv')
        parser.add_argument('--ignore-ids', action='store_true', help='Ignore Match_ID from CSV and generate new ones; write mapping to adminpanel/mappings/matches_map.csv')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        ignore_ids = kwargs.get('ignore_ids')
        mapping = []
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                match_date = None
                if row.get('Match_Date'):
                    try:
                        match_date = datetime.strptime(row.get('Match_Date'), '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Invalid date {row.get('Match_Date')}"))

                if ignore_ids:
                    m = Match(match_date=match_date, season=row.get('Season', ''))
                    m.save()
                    mapping.append({'old_id': row.get('Match_ID'), 'new_id': m.match_id})
                else:
                    Match.objects.update_or_create(
                        match_id=row.get('Match_ID'),
                        defaults={
                            'match_date': match_date,
                            'season': row.get('Season', ''),
                        }
                    )

        if ignore_ids and mapping:
            os.makedirs(os.path.join('adminpanel', 'mappings'), exist_ok=True)
            map_path = os.path.join('adminpanel', 'mappings', 'matches_map.csv')
            with open(map_path, 'w', newline='', encoding='utf-8') as mf:
                w = _csv.DictWriter(mf, fieldnames=['old_id', 'new_id'])
                w.writeheader()
                for r in mapping:
                    w.writerow(r)
            self.stdout.write(self.style.SUCCESS(f'Matches imported and mapping written to {map_path}'))
        else:
            self.stdout.write(self.style.SUCCESS('Matches imported successfully!'))
