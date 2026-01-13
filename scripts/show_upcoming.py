from datetime import date
from adminpanel.models import Match

today = date.today()
qs = Match.objects.filter(match_date__gte=today).order_by('match_date')[:20]
print('Total matches:', Match.objects.count())
print('Upcoming sample:')
for m in qs:
    print(m.match_date, m.match_time, m.opponent, m.location, m.league, m.outcome)
