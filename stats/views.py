from django.shortcuts import render
from django.http import JsonResponse
from adminpanel.models import Player, Match, MatchEvent

# HTML PAGE VIEW
def analytics_dashboard(request):
    players = Player.objects.all().order_by('surname', 'first_name')
    matches = Match.objects.all().order_by('-match_date')

    seasons = Match.objects.values_list('season', flat=True).distinct().order_by('season')
    event_types = MatchEvent.objects.values_list('event_type', flat=True).distinct().order_by('event_type')

    context = {
        "players": players,
        "matches": matches,
        "seasons": list(seasons),
        "event_types": list(event_types),
    }

    return render(request, "stats/analytics/index.html", context)


# JSON DATA ENDPOINT
def analytics_data(request):
    players = request.GET.getlist("players[]")
    matches = request.GET.getlist("matches[]")
    seasons = request.GET.getlist("seasons[]")
    event_types = request.GET.getlist("event_types[]")

    qs = MatchEvent.objects.select_related("player", "match")

    if players:
        qs = qs.filter(player_id__in=players)
    if matches:
        qs = qs.filter(match__match_id__in=matches)
    if seasons:
        qs = qs.filter(season__in=seasons)
    if event_types:
        qs = qs.filter(event_type__in=event_types)

    data = []
    for e in qs:
        data.append({
            "player_id": e.player_id,
            "player": f"{e.player.first_name} {e.player.surname}",
            "match_id": e.match.match_id,
            "match_date": str(e.match.match_date),
            "event_type": e.event_type,
            "minute": e.minute,
            "season": e.season,
        })

    return JsonResponse(data, safe=False)


# TEAM PLAYERS AUTO-FETCH
def players_for_match(request, match_id):
    events = MatchEvent.objects.filter(match_id=match_id).select_related("player")
    players = list({(e.player.id, f"{e.player.first_name} {e.player.surname}") for e in events})
    players_sorted = sorted(players, key=lambda x: x[1])
    return JsonResponse([{"id": p[0], "name": p[1]} for p in players_sorted], safe=False)
