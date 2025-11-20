"""
Stats app URL Configuration
"""
from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/players/', views.get_players, name='get_players'),
    path('api/player-stats/', views.get_player_stats, name='get_player_stats'),
    path('api/predict/', views.predict_match, name='predict_match'),
]
