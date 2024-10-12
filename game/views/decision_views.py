from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.bug import Bug
from ..utils import get_company_or_redirect, generate_random_bug
import random
from ..forms.decision_making_form import DecisionMakingForm

class DecisionMakingView(View):
    def get(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response

        form = DecisionMakingForm(initial={
            'status_report_frequency': company.status_report_frequency,
            'overtime_policy': company.overtime_policy
        })
        context = {
            'company': company,
            'form': form,
        }
        return render(request, 'game/decision_making.html', context)

    def post(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response

        form = DecisionMakingForm(request.POST)
        if form.is_valid():
            status_report_frequency = form.cleaned_data['status_report_frequency']
            overtime_policy = form.cleaned_data['overtime_policy']

            company.status_report_frequency = status_report_frequency
            company.overtime_policy = overtime_policy
            company.save()

            self.apply_decision_effects(company, status_report_frequency, overtime_policy)

            return redirect('game_loop')

        return render(request, 'game/decision_making.html', {'company': company, 'form': form})

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
                self.increase_bug_probability(company, 20)
            elif overtime_policy == 'optional':
                employee.productivity += 5
                employee.morale -= 2
                self.increase_bug_probability(company, 10)

            employee.save()

    def increase_bug_probability(self, company, bug_chance):
        projects = company.projects.all()
        for project in projects:
            features = project.features.all()
            for feature in features:
                generate_random_bug(project, feature, bug_chance)
