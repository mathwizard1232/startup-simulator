from django.shortcuts import render, redirect
from django.views import View
from .models import Company
import json

class DashboardView(View):
    def get(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        turn = request.session.get('turn', 1)

        # Prepare data for financial chart
        funds_history = json.loads(company.funds_history) if company.funds_history else []
        revenue_history = json.loads(company.revenue_history) if company.revenue_history else []
        
        # Add starting values if the histories are empty
        if not funds_history:
            funds_history = [float(company.funds)]
        if not revenue_history:
            revenue_history = [0]

        # Add current turn's values
        funds_history.append(float(company.funds))
        revenue_history.append(float(company.revenue))

        turn_numbers = list(range(1, len(funds_history) + 1))

        # Prepare data for project progress chart
        projects = company.projects.all()
        project_names = [project.name for project in projects]
        completed_features = [project.features.filter(state='COMPLETED').count() for project in projects]
        total_features = [project.features.count() for project in projects]
        incomplete_features = [total - completed for total, completed in zip(total_features, completed_features)]

        # Add a "No projects" entry if there are no projects
        if not projects:
            project_names = ["No projects"]
            completed_features = [0]
            incomplete_features = [0]

        context = {
            'company': company,
            'turn': turn,
            'turn_numbers': json.dumps(turn_numbers),
            'funds_history': json.dumps(funds_history),
            'revenue_history': json.dumps(revenue_history),
            'project_names': json.dumps(project_names),
            'completed_features': json.dumps(completed_features),
            'incomplete_features': json.dumps(incomplete_features),
        }

        return render(request, 'game/dashboard.html', context)