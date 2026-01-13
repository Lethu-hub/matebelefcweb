from django.urls import path
from . import views

urlpatterns = [
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("analytics/data/", views.analytics_data, name="analytics-data"),
    path("analytics/players_for_match/<int:match_id>/", views.players_for_match, name="players-for-match"),
]
