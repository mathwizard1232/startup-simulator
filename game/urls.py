from django.urls import path
from .views import StartGameView, GameLoopView, HireEmployeeView

urlpatterns = [
    path('', StartGameView.as_view(), name='start_game'),
    path('game/', GameLoopView.as_view(), name='game_loop'),
    path('hire/', HireEmployeeView.as_view(), name='hire_employee'),
]