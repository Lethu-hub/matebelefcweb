# adminpanel/urls.py
from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('players/', views.players_view, name='players'),
    path('players/delete/<str:pk>/', views.delete_player, name='delete_player'),
    path('matches/', views.matches_view, name='matches'),
    path('matches/add_players/', views.add_players_to_match, name='add_players_to_match'),
    path('matches/delete/<str:pk>/', views.delete_match, name='delete_match'),
    path('events/', views.events_view, name='events'),
    path('events/delete/<str:pk>/', views.delete_event, name='delete_event'),
]
