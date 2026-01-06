# adminpanel/forms.py
from django import forms
from .models import Player, Match, MatchEvent

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        widgets = {
            'match_date': forms.DateInput(attrs={'type': 'date'})
        }

class MatchEventForm(forms.ModelForm):
    class Meta:
        model = MatchEvent
        fields = '__all__'
