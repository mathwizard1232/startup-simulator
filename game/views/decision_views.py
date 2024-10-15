from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.bug import Bug
from ..utils import get_company_or_redirect, generate_random_bug
import random
from ..forms.decision_making_form import DecisionMakingForm
import logging

logger = logging.getLogger(__name__)

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
        logger.info("DecisionMakingView.post called")
        logger.info(f"DecisionMakingView.post request.POST: {request.POST}")
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            logger.info("DecisionMakingView.post redirecting")
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
        # TODO: fix how decision effects work: right now because they instantly take
        # effect, the player could just switch between weekly and monthly to keep
        # increasing productivity indefinitely.
        # Fix might be to instead store decisions and apply effects in game loop.
        # Alternately, undo effects of previous decisions before applying new ones.
        # Also, we update productivity based on decisions, but then we re-update it
        # based on morale, losing that effect. So again, storing decisions and applying
        # them in the game loop might be the best approach.
        employees = company.employees.all()

        for employee in employees:
            logger.info(f"Applying decision effects to employee {employee.name}")
            # Store previous values
            prev_morale = employee.morale
            prev_productivity = employee.productivity

            # Status report frequency affects productivity and morale
            if status_report_frequency == 'daily':
                employee.morale = max(1, employee.morale - 5)
                employee.productivity = max(1, employee.productivity - 10)
            elif status_report_frequency == 'weekly':
                employee.morale = min(100, employee.morale + 2)
                employee.productivity = min(100, employee.productivity + 5)
            elif status_report_frequency == 'monthly':
                employee.morale = max(1, employee.morale - 2)
                employee.productivity = min(100, employee.productivity + 10)

            # Overtime policy affects productivity, morale, and bug generation
            if overtime_policy == 'mandatory':
                employee.morale = max(1, employee.morale - 10)
                employee.productivity = min(100, employee.productivity + 15)
                self.increase_bug_probability(company, 20)
            elif overtime_policy == 'optional':
                employee.morale = max(1, employee.morale - 2)
                employee.productivity = min(100, employee.productivity + 5)
                self.increase_bug_probability(company, 10)

            # Update productivity based on new morale
            employee.update_productivity()

            # Log changes
            if employee.morale != prev_morale or employee.productivity != prev_productivity:
                logger.info(f"Employee {employee.name}: Morale changed from {prev_morale} to {employee.morale}, ")
                print(f"Employee {employee.name}: Morale changed from {prev_morale} to {employee.morale}, "
                      f"Productivity changed from {prev_productivity} to {employee.productivity}")

            employee.save()

    def increase_bug_probability(self, company, bug_chance):
        projects = company.projects.all()
        for project in projects:
            features = project.features.all()
            for feature in features:
                generate_random_bug(project, feature, bug_chance)
