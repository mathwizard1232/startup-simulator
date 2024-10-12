from django.urls import path
from .views.game_views import StartGameView, GameLoopView, EndGameView
from .views.employee_views import HireEmployeeView
from .views.project_views import CreateProjectView, ManageProjectView, AssignEmployeesView
from .views.decision_views import DecisionMakingView
from .views.dashboard_views import DashboardView

urlpatterns = [
    path('', StartGameView.as_view(), name='start_game'),
    path('game/', GameLoopView.as_view(), name='game_loop'),
    path('hire/', HireEmployeeView.as_view(), name='hire_employee'),
    path('create_project/', CreateProjectView.as_view(), name='create_project'),
    path('manage_project/<int:project_id>/', ManageProjectView.as_view(), name='manage_project'),
    path('decisions/', DecisionMakingView.as_view(), name='decision_making'),
    path('end_game/', EndGameView.as_view(), name='end_game'),
    path('assign_employees/<int:project_id>/', AssignEmployeesView.as_view(), name='assign_employees'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]