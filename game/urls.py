from django.urls import path
from .views.game_views import StartGameView, GameLoopView, EndGameView
from .views.employee_views import HireEmployeeView, EmployeeProfileView
from .views.project_views import CreateProjectView, ManageProjectView, AssignEmployeesView
from .views.decision_views import DecisionMakingView
from .views.dashboard_views import DashboardView

urlpatterns = [
    # Game flow
    path('', StartGameView.as_view(), name='start_game'),
    path('game/', GameLoopView.as_view(), name='game_loop'),
    path('end_game/', EndGameView.as_view(), name='end_game'),
    
    # Employee management
    path('hire/', HireEmployeeView.as_view(), name='hire_employee'),
    path('employee/<int:employee_id>/', EmployeeProfileView.as_view(), name='employee_profile'),
    
    # Project management
    path('create_project/', CreateProjectView.as_view(), name='create_project'),
    path('manage_project/<int:project_id>/', ManageProjectView.as_view(), name='manage_project'),
    path('assign_employees/<int:project_id>/', AssignEmployeesView.as_view(), name='assign_employees'),
    
    # Decision making and dashboard
    path('decisions/', DecisionMakingView.as_view(), name='decision_making'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
