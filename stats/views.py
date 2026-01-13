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


# METRICS ENDPOINT - histograms, cumulative series, top scorers
from django.db.models import Count
import math
from collections import defaultdict


def analytics_metrics(request):
    metric = request.GET.get('metric')  # e.g., 'minute_hist', 'cumulative_by_player', 'top_scorers'
    players = request.GET.getlist('players[]')
    matches = request.GET.getlist('matches[]')
    seasons = request.GET.getlist('seasons[]')
    event_types = request.GET.getlist('event_types[]')
    bins = int(request.GET.get('bins') or 10)

    qs = MatchEvent.objects.select_related('player', 'match')
    if players:
        qs = qs.filter(player_id__in=players)
    if matches:
        qs = qs.filter(match__match_id__in=matches)
    if seasons:
        qs = qs.filter(season__in=seasons)
    if event_types:
        qs = qs.filter(event_type__in=event_types)

    # MINUTE HISTOGRAM
    if metric == 'minute_hist' or metric == 'minute_density':
        minutes = [e.minute for e in qs if e.minute is not None]
        if not minutes:
            return JsonResponse({'labels': [], 'counts': []})
        mn = min(minutes)
        mx = max(minutes)
        if mn == mx:
            labels = [f"{mn}"]
            counts = [len(minutes)]
            if metric == 'minute_density':
                total = sum(counts)
                density = [c / total for c in counts]
                return JsonResponse({'labels': labels, 'density': density})
            return JsonResponse({'labels': labels, 'counts': counts})
        width = (mx - mn) / bins
        counts = [0] * bins
        edges = [mn + i * width for i in range(bins + 1)]
        for m in minutes:
            idx = min(int((m - mn) / width), bins - 1)
            counts[idx] += 1
        labels = [f"{math.floor(edges[i])}-{math.floor(edges[i+1])}" for i in range(bins)]
        if metric == 'minute_density':
            total = sum(counts)
            density = [ (c / total) / width for c in counts ]  # density per minute
            return JsonResponse({'labels': labels, 'density': density})
        return JsonResponse({'labels': labels, 'counts': counts})
    # CUMULATIVE BY MATCH (group by match date ordered)
    if metric == 'cumulative_by_player':
        # Build map match -> date, order by date
        matches_qs = Match.objects.filter(match_id__in=set([e.match.match_id for e in qs])).order_by('match_date')
        match_order = [m.match_id for m in matches_qs]
        labels = [str(m.match_date) + ' (' + m.match_id + ')' for m in matches_qs]
        datasets = []
        # Group by player
        players_set = players if players else list({e.player_id for e in qs})
        for pid in players_set:
            counts = []
            cum = 0
            for mid in match_order:
                c = qs.filter(player_id=pid, match__match_id=mid).count()
                cum += c
                counts.append(cum)
            name = (qs.filter(player_id=pid).first().player.first_name + ' ' + qs.filter(player_id=pid).first().player.surname) if qs.filter(player_id=pid).exists() else pid
            datasets.append({'label': name, 'data': counts})
        return JsonResponse({'labels': labels, 'datasets': datasets})

    # TOP SCORERS (count 'goal' events by player)
    if metric == 'top_scorers':
        goal_qs = qs.filter(event_type__icontains('goal'))
        top = goal_qs.values('player__first_name', 'player__surname').annotate(total=Count('id')).order_by('-total')[:10]
        labels = [f"{t['player__first_name']} {t['player__surname']}" for t in top]
        counts = [t['total'] for t in top]
        return JsonResponse({'labels': labels, 'counts': counts})

    return JsonResponse({'error': 'unknown metric'}, status=400)


# TEAM PLAYERS AUTO-FETCH
def players_for_match(request, match_id):
    events = MatchEvent.objects.filter(match_id=match_id).select_related("player")
    players = list({(e.player.id, f"{e.player.first_name} {e.player.surname}") for e in events})
    players_sorted = sorted(players, key=lambda x: x[1])
    return JsonResponse([{"id": p[0], "name": p[1]} for p in players_sorted], safe=False)

