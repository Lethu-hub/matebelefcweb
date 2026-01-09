import json
from django.shortcuts import render
from django.db.models import Count, Avg, StdDev, Variance
from adminpanel.models import Player, Match, MatchEvent

def analytics_dashboard(request):
    # Players
    players = Player.objects.annotate(
        total_events=Count('matchevent'),
        matches_played=Count('matchevent__match', distinct=True),
        mean_events=Avg('matchevent__minute'),
        variance=Variance('matchevent__minute'),
        std_dev=StdDev('matchevent__minute')
    ).order_by('surname', 'first_name')

    # Matches
    matches = Match.objects.annotate(
        total_events=Count('matchevent'),
        mean_events=Avg('matchevent__minute'),
        variance=Variance('matchevent__minute'),
        std_dev=StdDev('matchevent__minute')
    ).order_by('-match_date')

    # Seasons & Event Types
    seasons = Match.objects.values_list('season', flat=True).distinct().order_by('season')
    event_types = MatchEvent.objects.values_list('event_type', flat=True).distinct().order_by('event_type')

    # Build match -> player ids mapping
    match_players = {}
    for match in matches:
        player_ids = list(
            match.matchevent_set.values_list('player__player_id', flat=True).distinct()
        )
        match_players[match.match_id] = player_ids

    context = {
        'players': players,
        'matches': matches,
        'seasons': seasons,
        'event_types': event_types,
        'match_players_json': json.dumps(match_players)
    }

    return render(request, 'stats/analytics/index.html', context)
