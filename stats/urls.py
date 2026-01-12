from django.urls import path
from . import views

urlpatterns = [
    # HTML PAGE
    path("analytics/", views.analytics_dashboard, name="analytics"),

    # JSON DATA ENDPOINT (API)
    path("analytics/data/", views.analytics_data, name="analytics-data"),
]
