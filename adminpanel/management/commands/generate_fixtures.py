import random
from datetime import datetime, date, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from adminpanel.models import Match

OPPONENTS = [
    'Town United', 'Rovers FC', 'City Stars', 'Blue Eagles', 'Highlanders',
    'Santos', 'Lions', 'Rangers', 'United 88', 'Wanderers'
]
LOCATIONS = [
    'National Stadium', 'Central Park', 'Matebele Grounds', 'Riverside Arena',
    'Community Stadium', 'Township Field'
]

class Command(BaseCommand):
    help = 'Generate synthetic fixtures for upcoming matches for BFL and BPL'

    def add_arguments(self, parser):
        parser.add_argument('--per-league', type=int, default=30, help='Number of fixtures to create per league')
        parser.add_argument('--season', type=str, default=str(timezone.now().year), help='Season value to set on matches')

    def handle(self, *args, **kwargs):
        per_league = kwargs['per_league']
        season = kwargs['season']
        today = date.today()

        # league end dates: BPL end of March, BFL mid-April
        year = today.year
        bpl_end = date(year, 3, 31)
        bfl_end = date(year, 4, 15)

        created = 0
        for league, end_date in [('BPL', bpl_end), ('BFL', bfl_end)]:
            # spread fixtures between tomorrow and league end date
            start_date = today + timedelta(days=1)
            if start_date > end_date:
                self.stdout.write(self.style.WARNING(f"No future window for {league} in {year}. Skipping."))
                continue

            span_days = (end_date - start_date).days
            num = per_league
            for i in range(num):
                # pick a random day within the span
                d = start_date + timedelta(days=random.randint(0, max(0, span_days)))
                # random kickoff time between 12:00 and 20:00
                kickoff_hour = random.randint(12, 20)
                kickoff_minute = random.choice([0, 15, 30, 45])
                kickoff = time(kickoff_hour, kickoff_minute)

                opponent = random.choice(OPPONENTS)
                location = random.choice(LOCATIONS)

                # outcome: pending if future, else random
                match_dt = datetime.combine(d, kickoff)
                outcome = 'P' if match_dt.date() >= today else random.choice(['W', 'L', 'D'])

                m = Match(match_date=d, match_time=kickoff, season=season, opponent=opponent, location=location, outcome=outcome, league=league)
                m.save()
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} synthetic fixtures.'))
