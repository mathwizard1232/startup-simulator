from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.project import Project
from ..models.bug import Bug
import json
from decimal import Decimal
import random
from ..utils import generate_random_bug, progress_feature, fix_detected_bugs
from ..forms.start_game_form import StartGameForm
from game.utils.skill_utils import update_employee_perceptions
from django.contrib import messages

class StartGameView(View):
    def get(self, request):
        form = StartGameForm()
        return render(request, 'game/start_game.html', {'form': form})

    def post(self, request):
        form = StartGameForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.funds = Decimal('100000')  # $100,000 initial funding
            company.save()
            request.session['company_id'] = company.id
            request.session['turn'] = 1
            return redirect('game_loop')
        return render(request, 'game/start_game.html', {'form': form})

class GameLoopView(View):
    def get(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            # If no company_id in session, check if there's an active company
            active_company = Company.objects.filter(game_status='ONGOING').first()
            if active_company:
                # If there's an active company, set it in the session
                request.session['company_id'] = active_company.id
                company_id = active_company.id
            else:
                # If no active company, redirect to start game
                return redirect('start_game')

        company = Company.objects.get(id=company_id)
        employees = company.employees.all()
        projects = company.projects.all()
        turn = request.session.get('turn', 1)

        context = {
            'company': company,
            'employees': employees,
            'projects': projects,
            'turn': turn,
        }

        return render(request, 'game/game_loop.html', context)

    def post(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)

        action = request.POST.get('action')
        if action == 'end_day':
            self.advance_time(company, 1)
        elif action == 'end_week':
            self.advance_time(company, 5) # 5 business days per week
        elif action == 'end_month':
            self.advance_time(company, 23) # 23ish business days per month

        # Increment turn count and update session
        turn = request.session.get('turn', 1)
        turn += 1
        request.session['turn'] = turn

        if company.game_status == 'LOST':
            return redirect('end_game')

        # Check win condition
        if company.funds >= 1000000:  # $1 million
            company.game_status = 'WON'
            company.save()
            return redirect('end_game')

        return redirect('game_loop')

    def advance_time(self, company, days):
        for _ in range(days):
            self.process_turn(company)
            if company.game_status == 'LOST':
                break
        
        # Ensure we end on a business day
        while not company.is_workday:
            self.process_turn(company)
            if company.game_status == 'LOST':
                break

    def process_turn(self, company):
        """
        Process a single day for the company.
        """
        company.advance_time(1)
        self.generate_revenue(company)
        continue_game = self.deduct_salaries(company)
        self.update_historical_data(company)
        if not continue_game:
            return False
        
        if company.is_workday:
            self.process_projects(company)
        
        return True

    def deduct_salaries(self, company):
        """
        Deduct employee salaries from company funds.
        Returns False if company funds become negative, True otherwise.
        """
        total_salary = sum(employee.salary for employee in company.employees.all())
        company.funds -= Decimal(total_salary) / Decimal('365')  # Daily salary

        if company.funds < 0:
            company.game_status = 'LOST'
            company.save()
            return False
        return True

    def process_projects(self, company):
        """
        Process all projects with assigned employees.
        """
        for project in company.projects.all():
            if project.employees.exists():
                self.process_project(project)

    def generate_revenue(self, company):
        """
        Generate daily revenue from completed projects.
        """
        for project in company.projects.all():
            if project.state == 'COMPLETED':
                daily_revenue = (Decimal('50000') * Decimal(project.complexity)) / Decimal('365')
                company.funds += daily_revenue
                company.revenue += daily_revenue
        company.save()

    def update_historical_data(self, company):
        """
        Update historical data for funds and revenue.
        """
        funds_history = json.loads(company.funds_history)
        revenue_history = json.loads(company.revenue_history)
        funds_history.append(float(company.funds))
        revenue_history.append(float(company.revenue))
        company.funds_history = json.dumps(funds_history)
        company.revenue_history = json.dumps(revenue_history)
        company.save()

    def process_project(self, project):
        employees = project.employees.all()
        features = project.features.filter(state__in=['NOT_STARTED', 'IN_PROGRESS', 'TESTING'])

        # Don't get stuck if assigned employees but no features to work on
        if not features:
            # TODO: still could have employees work on detecting / fixing bugs
            return
        
        # Determine effective skill for each feature
        feature_skills = {}
        remaining_employees = list(employees)
        
        for feature in features:
            if not remaining_employees:
                break
            
            feature_skills[feature] = remaining_employees.pop(0).coding_accuracy
        
        # Distribute remaining employees
        while remaining_employees:
            for feature in feature_skills:
                if not remaining_employees:
                    break
                current_skill = feature_skills[feature]
                additional_skill = remaining_employees.pop(0).coding_accuracy
                # Cap at 14 skill level - higher than individual but still imperfect
                feature_skills[feature] = max(14, current_skill + 0.5 * additional_skill)
        
        total_progress = 0
        total_bugs = 0
        for feature, skill in feature_skills.items():
            progress_chance = min(skill * 5, 95)
            progress, bugs = self.process_feature(feature, project, progress_chance)
            total_progress += progress
            total_bugs += bugs
        
        # Calculate project success based on progress and bugs
        project_success = total_progress / len(features) - (total_bugs * 0.1)
        
        # Update employee perceptions
        for employee in employees:
            updates = update_employee_perceptions(employee, project_success, total_bugs, len(employees))
            if updates:
                messages.info(self.request, f"{employee.name}'s perceived {', '.join(updates)} has been updated.")

        # TODO: updates if the project is completed?
        # Currently this is a computed property, so result not stored.

    def process_feature(self, feature, project, progress_chance):
        if feature.state == 'NOT_STARTED':
            self.start_feature(feature, project, progress_chance)
            return 1, 0  # We can always start and no bugs are detected
        else:
            return progress_feature(feature, progress_chance)

    def start_feature(self, feature, project, progress_chance):
        feature.state = 'IN_PROGRESS'
        generate_random_bug(project, feature, 100 - progress_chance)
        feature.save()

class EndGameView(View):
    def get(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        context = {
            'company': company,
            'game_status': company.game_status,
        }
        return render(request, 'game/end_game.html', context)
