from django.shortcuts import render, redirect
from django.views import View
from .models.company import Company
from .models.bug import Bug
import random

class DecisionMakingView(View):
    def get(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        projects = company.projects.all()
        employees = company.employees.all()

        context = {
            'company': company,
            'projects': projects,
            'employees': employees,
        }

        return render(request, 'game/decision_making.html', context)

    def post(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        
        # Process micromanagement decisions
        status_report_frequency = request.POST.get('status_report_frequency')
        overtime_policy = request.POST.get('overtime_policy')

        # Update company policies
        company.status_report_frequency = status_report_frequency
        company.overtime_policy = overtime_policy
        company.save()

        # Apply effects of decisions
        self.apply_decision_effects(company, status_report_frequency, overtime_policy)

        return redirect('game_loop')

    def apply_decision_effects(self, company, status_report_frequency, overtime_policy):
        employees = company.employees.all()
        
        for employee in employees:
            # Status report frequency affects productivity and morale
            if status_report_frequency == 'daily':
                employee.productivity -= 10
                employee.morale -= 5
            elif status_report_frequency == 'weekly':
                employee.productivity += 5
                employee.morale += 2
            elif status_report_frequency == 'monthly':
                employee.productivity += 10
                employee.morale -= 2

            # Overtime policy affects productivity, morale, and bug generation
            if overtime_policy == 'mandatory':
                employee.productivity += 15
                employee.morale -= 10
                self.increase_bug_probability(company, 0.2)
            elif overtime_policy == 'optional':
                employee.productivity += 5
                employee.morale -= 2
                self.increase_bug_probability(company, 0.1)

            employee.save()

    def increase_bug_probability(self, company, factor):
        projects = company.projects.all()
        for project in projects:
            features = project.features.all()
            for feature in features:
                if random.random() < factor:
                    Bug.objects.create(
                        description=f"New bug in {feature.name}",
                        project=project,
                        state='UNDETECTED'
                    )