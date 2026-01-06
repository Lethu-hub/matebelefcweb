# adminpanel/urls.py
from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('players/', views.players_view, name='players'),
    path('players/delete/<uuid:pk>/', views.delete_player, name='delete_player'),
    path('matches/', views.matches_view, name='matches'),
    path('matches/delete/<uuid:pk>/', views.delete_match, name='delete_match'),
    path('events/', views.events_view, name='events'),
    path('events/delete/<uuid:pk>/', views.delete_event, name='delete_event'),
]
