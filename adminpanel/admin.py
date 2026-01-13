from django.contrib import admin
from .models import Player, Match, MatchEvent, EventType
from django import forms
import pandas as pd
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import redirect
from io import StringIO

# ---------------- Player Admin ----------------
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'surname', 'player_id')
    change_list_template = "admin/player_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv),
            path('export-csv/', self.export_csv),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                Player.objects.update_or_create(
                    player_id=row['player_id'],
                    defaults={
                        'first_name': row['first_name'],
                        'surname': row['surname'],
                    }
                )
            self.message_user(request, "Players imported successfully.")
            return redirect("..")
        return HttpResponse("""
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <input type="file" name="csv_file" accept=".csv">
                <button type="submit">Upload CSV</button>
            </form>
        """)

    def export_csv(self, request):
        players = Player.objects.all().values('player_id', 'first_name', 'surname')
        df = pd.DataFrame(players)
        response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=players.csv'
        return response

# ---------------- Match Admin ----------------
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'match_date', 'season')
    change_list_template = "admin/match_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv),
            path('export-csv/', self.export_csv),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                Match.objects.update_or_create(
                    match_id=row['match_id'],
                    defaults={
                        'match_date': row['match_date'],
                        'season': row['season'],
                    }
                )
            self.message_user(request, "Matches imported successfully.")
            return redirect("..")
        return HttpResponse("""
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <input type="file" name="csv_file" accept=".csv">
                <button type="submit">Upload CSV</button>
            </form>
        """)

    def export_csv(self, request):
        matches = Match.objects.all().values('match_id', 'match_date', 'season')
        df = pd.DataFrame(matches)
        response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=matches.csv'
        return response

# ---------------- MatchEvent Admin ----------------
@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'event_type', 'minute')
    change_list_template = "admin/matchevent_change_list.html"

    class MatchEventForm(forms.ModelForm):
        event_type = forms.ChoiceField(required=False)

        class Meta:
            model = MatchEvent
            fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # populate choices from EventType table
            choices = [(et.name, et.name) for et in EventType.objects.all()]
            choices.insert(0, ('', '---'))
            self.fields['event_type'].choices = choices

    form = MatchEventForm

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv),
            path('export-csv/', self.export_csv),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                MatchEvent.objects.update_or_create(
                    match_id=row['match_id'],
                    player_id=row['player_id'],
                    event_type=row['event_type'],
                    minute=row['minute']
                )
            self.message_user(request, "MatchEvents imported successfully.")
            return redirect("..")
        return HttpResponse("""
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <input type="file" name="csv_file" accept=".csv">
                <button type="submit">Upload CSV</button>
            </form>
        """)

    def export_csv(self, request):
        events = MatchEvent.objects.all().values('match_id', 'player_id', 'event_type', 'minute')
        df = pd.DataFrame(events)
        response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=matchevents.csv'
        return response


# Register EventType for create/edit in admin
@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
