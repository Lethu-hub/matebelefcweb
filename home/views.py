from django.shortcuts import render
from adminpanel.models import Match
from datetime import date
from django.db.models import Count


def index(request):
    today = date.today()
    all_upcoming = list(Match.objects.filter(match_date__gte=today).order_by('match_date', 'match_time'))
    upcoming_matches = all_upcoming[:5]
    upcoming_rest = all_upcoming[5:]

    # overall counts
    games_played = Match.objects.filter(match_date__lt=today).count()
    total_matches = Match.objects.exclude(match_date__isnull=True).count()
    upcoming_count = Match.objects.filter(match_date__gte=today).count()

    # per-season breakdown
    seasons = Match.objects.exclude(season='').values('season').annotate(total=Count('match_id')).order_by('season')
    season_stats = []
    for s in seasons:
        season = s['season']
        total = s['total']
        played = Match.objects.filter(season=season, match_date__lt=today).count()
        upcoming = Match.objects.filter(season=season, match_date__gte=today).count()
        season_stats.append({'season': season, 'total': total, 'played': played, 'upcoming': upcoming})

    # fixtures removed from homepage; keep fixtures logic elsewhere if needed

    context = {
        'upcoming_matches': upcoming_matches,
        'upcoming_rest': upcoming_rest,
        'games_played': games_played,
        'total_matches': total_matches,
        'upcoming_count': upcoming_count,
        'season_stats': season_stats,
    }

    return render(request, 'home/index.html', context)