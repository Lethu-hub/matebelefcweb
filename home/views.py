from django.shortcuts import render
from adminpanel.models import Match
from datetime import date

def index(request):
    today = date.today()
    upcoming_matches = Match.objects.filter(match_date__gte=today).order_by('match_date')[:5]
    games_played = Match.objects.filter(match_date__lt=today).count()
    total_matches = Match.objects.exclude(match_date__isnull=True).count()
    upcoming_count = Match.objects.filter(match_date__gte=today).count()

    context = {
        'upcoming_matches': upcoming_matches,
        'games_played': games_played,
        'total_matches': total_matches,
        'upcoming_count': upcoming_count,
    }

    return render(request, 'home/index.html', context)