from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.project import Project
from ..models.bug import Bug
import json
from decimal import Decimal
import random
from ..utils import generate_random_bug, progress_feature, fix_detected_bugs

class StartGameView(View):
    def get(self, request):
        return render(request, 'game/start_game.html')

    def post(self, request):
        company_name = request.POST.get('company_name')
        initial_funds = 100000  # $100,000 initial funding

        industry = request.POST.get('industry')
        
        if not company_name or not industry:
            return render(request, 'game/start_game.html', {'error': 'Please provide both company name and industry.'})

        company = Company.objects.create(
            name=company_name,
            funds=initial_funds,  # Starting funds
            industry=industry
        )
        request.session['company_id'] = company.id
        request.session['turn'] = 1

        return redirect('game_loop')

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

        # Process turn actions
        game_continues = self.process_turn(company)

        if not game_continues:
            return redirect('end_game')

        # Check win condition
        if company.funds >= 1000000:  # $1 million
            company.game_status = 'WON'
            company.save()
            return redirect('end_game')

        # Process turn actions here
        # For now, just increment the turn counter
        request.session['turn'] = request.session.get('turn', 1) + 1
        return redirect('game_loop')

    def process_turn(self, company):
        """
        Process a single turn for the company.
        Returns True if the game should continue, False if the company has lost.
        """
        if not self.deduct_salaries(company):
            return False

        self.process_projects(company)
        self.generate_revenue(company)
        self.update_historical_data(company)
        
        return True

    def deduct_salaries(self, company):
        """
        Deduct employee salaries from company funds.
        Returns False if company funds become negative, True otherwise.
        """
        total_salary = sum(employee.salary for employee in company.employees.all())
        company.funds -= Decimal(total_salary) / Decimal('52')  # Assuming weekly turns and annual salary

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
        Generate revenue from completed projects.
        """
        for project in company.projects.all():
            if project.state == 'COMPLETED':
                revenue = Decimal('10000') * Decimal(project.complexity)
                company.funds += revenue
                company.revenue += revenue
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
        #TODO: we should eventually have an employee on one feature at a time
        employees = project.employees.all()
        if not employees:
            return  # No progress if no employees assigned

        progress_chance = self.calculate_progress_chance(employees)

        for feature in project.features.exclude(state='COMPLETED'):
            self.process_feature(feature, project, progress_chance)

        fix_detected_bugs(project, progress_chance)
        project.save()

    def calculate_progress_chance(self, employees):
        total_skill = sum(employee.skill_level for employee in employees)
        # TODO: diminishing returns when combining employees, scaled by teamwork
        # Especially bad if number of teammates exceeds number of features
        return min(total_skill * 5, 95)  # Cap at 95% - always leave room for bugs

    def process_feature(self, feature, project, progress_chance):
        if feature.state == 'NOT_STARTED':
            self.start_feature(feature, project, progress_chance)
        else:
            progress_feature(feature, progress_chance)

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
