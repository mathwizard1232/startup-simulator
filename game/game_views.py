from django.shortcuts import render, redirect
from django.views import View
from .models import Company, Project, Bug
import json
from decimal import Decimal
import random

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
        # Deduct employee salaries
        total_salary = sum(employee.salary for employee in company.employees.all())
        company.funds -= Decimal(total_salary) / Decimal('52')  # Assuming weekly turns and annual salary

        # Check if funds are negative
        if company.funds < 0:
            company.game_status = 'LOST'
            company.save()
            return False  # Return False to indicate game over

        # Process projects
        for project in company.projects.all():
            if project.employees.exists():
                self.process_project(project)
            else:
                # Optionally, you could add some penalty for unattended projects
                pass

        # Generate revenue from completed projects
        completed_projects = [project for project in company.projects.all() if project.state == 'COMPLETED']
        for project in completed_projects:
            revenue = Decimal('10000') * Decimal(project.complexity)
            company.funds += revenue
            company.revenue += revenue

        # Update historical data
        funds_history = json.loads(company.funds_history)
        revenue_history = json.loads(company.revenue_history)
        funds_history.append(float(company.funds))
        revenue_history.append(float(company.revenue))
        company.funds_history = json.dumps(funds_history)
        company.revenue_history = json.dumps(revenue_history)
        company.save()
        return True  # Return True to indicate the game should continue

    def process_project(self, project):
        employees = project.employees.all()
        if not employees:
            return  # No progress if no employees assigned

        total_skill = sum(employee.skill_level for employee in employees)
        progress_chance = min(total_skill * 5, 100)  # Cap at 100%

        for feature in project.features.exclude(state='COMPLETED'):
            if random.randint(1, 100) <= progress_chance:
                if feature.state == 'NOT_STARTED':
                    feature.state = 'IN_PROGRESS'
                    # Chance to introduce bugs during development
                    if random.randint(1, 100) <= 30:  # 30% chance of creating a bug
                        Bug.objects.create(project=project, feature=feature, description="Hidden bug", state='UNDETECTED')
                elif feature.state == 'IN_PROGRESS':
                    feature.state = 'TESTING'
                elif feature.state == 'TESTING':
                    # Chance to detect existing bugs
                    for bug in feature.bugs.filter(state='UNDETECTED'):
                        if random.randint(1, 100) <= progress_chance:
                            bug.detected = True
                            bug.save()
                    
                    if not feature.bugs.filter(state='DETECTED').exists():
                        feature.state = 'COMPLETED'
                feature.save()
        # Fix detected bugs
        for bug in Bug.objects.filter(feature__project=project, state='DETECTED'):
            if random.randint(1, 100) <= progress_chance:
                # Chance to introduce new bug while fixing
                if random.randint(1, 100) <= 10:  # 10% chance of creating a new bug
                    Bug.objects.create(project=bug.project, feature=bug.feature, description="Bug introduced during fix", state='UNDETECTED')
                bug.delete()

        project.save()

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
