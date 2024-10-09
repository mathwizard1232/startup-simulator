from django.urls import path
from .views import StartGameView, GameLoopView

urlpatterns = [
    path('', StartGameView.as_view(), name='start_game'),
    path('game/', GameLoopView.as_view(), name='game_loop'),
]