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
import logging
from ..models.hiringprocess import HiringProcess
from ..utils.employee_utils import create_employee

logger = logging.getLogger(__name__)

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
        hiring_processes = HiringProcess.objects.filter(company=company).exclude(employee__isnull=False)
        logger.info(f"Number of hiring processes: {hiring_processes.count()}")
        employees = company.employees.all()
        projects = company.projects.all()
        turn = request.session.get('turn', 1)

        context = {
            'company': company,
            'employees': employees,
            'projects': projects,
            'turn': turn,
            'hiring_processes': hiring_processes,
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

    @classmethod  # class method to allow hiring to call directly for resume_only
    def process_hiring(cls, company):
        completed_hiring = HiringProcess.objects.filter(
            company=company,
            employee__isnull=True,
            expected_hire_date__lte=company.current_date
        )
        
        for hiring in completed_hiring:
            create_employee(hiring)

    def process_turn(self, company):
        """
        Process a single day for the company.
        """
        company.advance_time(1)
        self.generate_revenue(company)
        continue_game = self.deduct_salaries(company)
        self.process_hiring(company)
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
        feature_speed = {}
        feature_accuracy = {}
        feature_debugging = {}
        feature_productivity = {}
        feature_teamwork = {}
        feature_traits = {}
        remaining_employees = list(employees)
        
        # Assign an initial employee to each feature, if there are enough employees
        for feature in features:
            if not remaining_employees:
                break
            employee = remaining_employees.pop(0)
            logger.info(f"Assigning employee {employee.name} with {employee.personality_traits} and {employee.coding_speed}, {employee.coding_accuracy}, {employee.debugging}, {employee.teamwork} to feature {feature.name}")
            feature_speed[feature] = employee.coding_speed
            feature_accuracy[feature] = employee.coding_accuracy
            feature_debugging[feature] = employee.debugging
            feature_teamwork[feature] = employee.teamwork
            # For now we'll just use the first employee's productivity for the feature
            # TODO: actually calculate feature productivity based on team skills
            feature_productivity[feature] = employee.productivity
            feature_traits[feature] = employee.personality_traits
        # Distribute remaining employees
        while remaining_employees:
            for feature in feature_speed:
                if not remaining_employees:
                    break
                current_speed = feature_speed[feature]
                current_accuracy = feature_accuracy[feature]
                current_debugging = feature_debugging[feature]
                new_employee = remaining_employees.pop(0)
                additional_speed = new_employee.coding_speed
                additional_accuracy = new_employee.coding_accuracy
                additional_debugging = new_employee.debugging
                # Team's teamwork skill is the highest individual skill
                teamwork = max(feature_teamwork[feature], new_employee.teamwork)
                # Speed is the hardest to increase with more people
                # Perfect teamwork allows 25% increase at most
                speed_factor = Decimal(0.25) * Decimal(teamwork) / Decimal(10)
                # Accuracy is easier to increase with more people
                accuracy_factor = Decimal(0.5) * Decimal(teamwork) / Decimal(10)
                debugging_factor = accuracy_factor
                # Cap at 16 skill level - higher than individual but still imperfect
                feature_speed[feature] = max(16, current_speed + speed_factor * additional_speed)
                feature_accuracy[feature] = max(16, current_accuracy + accuracy_factor * additional_accuracy)
                feature_debugging[feature] = max(16, current_debugging + debugging_factor * additional_debugging)
                feature_traits[feature] = feature_traits[feature].append(new_employee.personality_traits)
        
        total_progress = 0
        total_bugs = 0
        for feature, speed_skill in feature_speed.items():
            if 'meme_lord' in feature_traits[feature]:
                feature_productivity[feature] += 10
            # Always some chance not to make progress
            logger.info(f"Feature {feature.name} has speed skill {speed_skill} and productivity {feature_productivity[feature]}")
            progress_chance = min(speed_skill * 7.5 * feature_productivity[feature] / 100, 95)
            # Always some chance to produce a bug
            bug_chance = max(100 - feature_accuracy[feature] * 7.5, 5)
            debugging_chance = min(feature_debugging[feature] * 7.5, 95)
            if 'perfectionist' in feature_traits[feature]:
                # Subtract 10% from bug chance if there's a perfectionist on the feature
                bug_chance = max(bug_chance - 10, 5)
                # But less likely to make progress
                progress_chance *= 0.85
            if 'rubber_duck_whisperer' in feature_traits[feature]:
                debugging_chance += 15
            if 'stack_overflow_junkie' in feature_traits[feature]:
                # 50% chance to solve bugs instantly
                # 10% chance to introduce new bugs
                if random.randint(1, 100) <= 50:
                    bugs = fix_detected_bugs(feature.project, 100)
                elif random.randint(1, 100) <= 20:
                    # Because only a 50% chance to evaluate above, there's a 10% chance overall
                    generate_random_bug(feature.project, feature, 100)
            progress, bugs = self.process_feature(feature=feature, project=project, progress_chance=progress_chance, bug_chance=bug_chance, debugging_chance=debugging_chance)
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

    def process_feature(self, feature, project, progress_chance, bug_chance, debugging_chance):
        logger.info(f"Processing feature {feature.name} with state {feature.state} and {progress_chance} progress chance, {bug_chance} bug chance, and {debugging_chance} debugging chance")
        if feature.state == 'NOT_STARTED':
            self.start_feature(feature, project, bug_chance=bug_chance)
            return 1, 0  # We can always start and no bugs are detected
        else:
            return progress_feature(feature=feature, progress_chance=progress_chance, bug_chance=bug_chance, debugging_chance=debugging_chance)

    def start_feature(self, feature, project, bug_chance):
        feature.state = 'IN_PROGRESS'
        generate_random_bug(project, feature, bug_chance)
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
