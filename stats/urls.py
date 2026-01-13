from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("analytics/data/", views.analytics_data, name="analytics-data"),
    path("analytics/metrics/", views.analytics_metrics, name="analytics-metrics"),
    path("analytics/players_for_match/<str:match_id>/", views.players_for_match, name="players-for-match"),
]
