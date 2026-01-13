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
        goal_qs = qs.filter(event_type__icontains='goal')
        top = goal_qs.values('player__first_name', 'player__surname').annotate(total=Count('id')).order_by('-total')[:10]
        labels = [f"{t['player__first_name']} {t['player__surname']}" for t in top]
        counts = [t['total'] for t in top]
        return JsonResponse({'labels': labels, 'counts': counts})

    # GOALS PER PLAYER ACROSS SEASONS (cumulative bar)
    if metric == 'goals_per_player_season':
        goal_qs = qs.filter(event_type__icontains='goal')
        by_player = goal_qs.values('player__player_id', 'player__first_name', 'player__surname').annotate(total=Count('id')).order_by('-total')[:10]
        labels = [f"{b['player__first_name']} {b['player__surname']}" for b in by_player]
        counts = [b['total'] for b in by_player]
        return JsonResponse({'labels': labels, 'counts': counts})

    # SCATTER: event minutes in a season
    if metric == 'scatter_minutes_season':
        points = []
        for e in qs:
            if e.minute is not None:
                points.append({'x': e.minute, 'player_id': e.player_id, 'player': f"{e.player.first_name} {e.player.surname}"})
        return JsonResponse({'points': points})

    # LINE: goals per match over time
    if metric == 'goals_per_match_time_series':
        matches_qs = Match.objects.filter(match_id__in=set([e.match.match_id for e in qs])).order_by('match_date')
        labels = [str(m.match_date) for m in matches_qs]
        counts = []
        for m in matches_qs:
            c = qs.filter(match__match_id=m.match_id, event_type__icontains='goal').count()
            counts.append(c)
        return JsonResponse({'labels': labels, 'counts': counts})

    # STACKED BAR: event types per player
    if metric == 'stacked_event_types_per_player':
        # choose top 5 event types
        types = list(MatchEvent.objects.values_list('event_type', flat=True).distinct())[:5]
        players = list({e.player_id for e in qs})
        labels = []
        datasets = []
        for pid in players:
            try:
                labels.append(qs.filter(player_id=pid).first().player.first_name + ' ' + qs.filter(player_id=pid).first().player.surname)
            except:
                labels.append(pid)
        for t in types:
            data = [qs.filter(player_id=pid, event_type=t).count() for pid in players]
            datasets.append({'label': t, 'data': data})
        return JsonResponse({'labels': labels, 'datasets': datasets})

    # HISTOGRAM: player ages in a season (not available if no birthdate)
    if metric == 'player_age_histogram':
        # player model does not have birthdate in current schema
        return JsonResponse({'labels': [], 'counts': []})

    # MULTI-LINE: team goals vs opponent goals across matches
    if metric == 'team_vs_opponent_goals':
        matches_qs = Match.objects.filter(match_id__in=set([e.match.match_id for e in qs])).order_by('match_date')
        labels = [str(m.match_date) for m in matches_qs]
        team = []
        opp = []
        for m in matches_qs:
            team_goals = qs.filter(match__match_id=m.match_id, event_type__icontains='goal').exclude(event_type__icontains='against').count()
            opp_goals = qs.filter(match__match_id=m.match_id, event_type__icontains='goal').filter(event_type__icontains='against').count()
            team.append(team_goals)
            opp.append(opp_goals)
        datasets = [{'label': 'Matebele FC', 'data': team}, {'label': 'Opponent', 'data': opp}]
        return JsonResponse({'labels': labels, 'datasets': datasets})

    # PIE: event type distribution in a match (requires ?match_id=)
    if metric == 'event_type_pie':
        match_id = request.GET.get('match_id')
        if not match_id:
            return JsonResponse({'labels': [], 'counts': []})
        evs = MatchEvent.objects.filter(match__match_id=match_id)
        agg = evs.values('event_type').annotate(count=Count('id')).order_by('-count')
        labels = [a['event_type'] for a in agg]
        counts = [a['count'] for a in agg]
        return JsonResponse({'labels': labels, 'counts': counts})

    # HEATMAP: event frequency by minute interval
    if metric == 'minute_interval_heatmap':
        intervals = ['0-15','16-30','31-45','46-60','61-75','76-90','90+']
        edges = [(0,15),(16,30),(31,45),(46,60),(61,75),(76,90),(91,1000)]
        counts = [0]*len(edges)
        for e in qs:
            if e.minute is None:
                continue
            m = e.minute
            for i,(lo,hi) in enumerate(edges):
                if lo <= m <= hi:
                    counts[i] += 1
                    break
        return JsonResponse({'labels': intervals, 'counts': counts})

    # GROUPED BAR: goals per position
    if metric == 'goals_per_position':
        goal_qs = qs.filter(event_type__icontains='goal')
        pos_counts = goal_qs.values('player__position').annotate(total=Count('id')).order_by('-total')
        labels = [p['player__position'] or 'Unknown' for p in pos_counts]
        counts = [p['total'] for p in pos_counts]
        return JsonResponse({'labels': labels, 'counts': counts})

    # CUMULATIVE: matches played per player in a season
    if metric == 'matches_played_cumulative':
        season = request.GET.get('season')
        players = Player.objects.all()
        counts = []
        for p in players:
            q = Match.objects.filter(players=p)
            if season:
                q = q.filter(season=season)
            counts.append(q.count())
        counts_sorted = sorted(counts)
        # cumulative frequency
        labels = list(range(1, max(counts_sorted)+1)) if counts_sorted else []
        freq = [sum(1 for c in counts_sorted if c<=i) for i in labels]
        return JsonResponse({'labels': labels, 'counts': freq})

    return JsonResponse({'error': 'unknown metric'}, status=400)


# TEAM PLAYERS AUTO-FETCH
def players_for_match(request, match_id):
    events = MatchEvent.objects.filter(match__match_id=match_id).select_related("player")
    players = list({(e.player.player_id, f"{e.player.first_name} {e.player.surname}") for e in events})
    players_sorted = sorted(players, key=lambda x: x[1])
    return JsonResponse([{"id": p[0], "name": p[1]} for p in players_sorted], safe=False)

