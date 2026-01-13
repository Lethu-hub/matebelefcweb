# adminpanel/views.py
from django.shortcuts import render, redirect
from .models import Player, Match, MatchEvent
from .forms import PlayerForm, MatchForm, MatchEventForm

# ---------------- Player ----------------
def players_view(request):
    form = PlayerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('adminpanel:players')
    
    players = Player.objects.all()
    return render(request, 'adminpanel/players/index.html', {'form': form, 'players': players})

def delete_player(request, pk):
    Player.objects.filter(player_id=pk).delete()
    return redirect('adminpanel:players')

# ---------------- Match ----------------
def matches_view(request):
    form = MatchForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('adminpanel:matches')
    
    matches = Match.objects.all()
    players = Player.objects.all().order_by('surname', 'first_name')
    return render(request, 'adminpanel/matches/index.html', {'form': form, 'matches': matches, 'players': players})


def add_players_to_match(request):
    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        player_ids = request.POST.getlist('players')
        try:
            m = Match.objects.get(match_id=match_id)
            # player_ids are UUID strings -> add by pk
            players_qs = Player.objects.filter(player_id__in=player_ids)
            m.players.add(*players_qs)
        except Match.DoesNotExist:
            pass
    return redirect('adminpanel:matches')

def delete_match(request, pk):
    Match.objects.filter(match_id=pk).delete()
    return redirect('adminpanel:matches')

# ---------------- Match Event ----------------
def events_view(request):
    form = MatchEventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('adminpanel:events')
    
    events = MatchEvent.objects.all()
    return render(request, 'adminpanel/match_events/index.html', {'form': form, 'events': events})

def delete_event(request, pk):
    MatchEvent.objects.filter(pk=pk).delete()
    return redirect('adminpanel:events')
