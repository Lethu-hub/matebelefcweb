from django.urls import path
from . import views

app_name = "stats"

urlpatterns = [
    path('analytics/', views.analytics_dashboard, name='analytics'),
]
