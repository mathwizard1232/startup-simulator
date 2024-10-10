from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Company, Employee, Project, Feature, Bug
import random
from decimal import Decimal
import json
from django.db.models import Count

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
        turn = request.session.get('turn', 1)

        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        
        if company.game_status != 'ONGOING':
            return redirect('end_game')

        employees = company.employees.all()
        projects = company.projects.all()

        context = {
            'company': company,
            'employees': employees,
            'projects': projects,
            'turn': turn,
        }

        return render(request, 'game/game_loop.html', context)

    def post(self, request):
        company_id = request.session.get('company_id')
        company = Company.objects.get(id=company_id)

        # Process turn actions
        self.process_turn(company)

        # Check win condition
        if company.funds >= 1000000:  # $1 million
            company.game_status = 'WON'
            company.save()
            return redirect('end_game')

        # Check lose condition
        if company.funds <= 0:
            company.game_status = 'LOST'
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

        # Process projects
        for project in company.projects.all():
            self.process_project(project)

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

class HireEmployeeView(View):
    def get(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        return render(request, 'game/hire_employee.html', {'company': company})

    def post(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        employee_type = request.POST.get('employee_type')

        if employee_type == 'perfectionist':
            is_perfectionist = True
            skill_level = random.randint(7, 10)
            salary = random.randint(80000, 120000)
        else:
            is_perfectionist = False
            skill_level = random.randint(5, 8)
            salary = random.randint(60000, 90000)

        employee = Employee.objects.create(
            name=f"Employee {company.employees.count() + 1}",
            is_perfectionist=is_perfectionist,
            skill_level=skill_level,
            salary=salary,
            company=company
        )

        # Deduct only the first week's salary
        weekly_salary = Decimal(salary) / Decimal('52')
        company.funds -= weekly_salary
        company.save()

        return redirect('game_loop')

class CreateProjectView(View):
    def get(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')
        company = Company.objects.get(id=company_id)
        return render(request, 'game/create_project.html', {'company': company})

    def post(self, request):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')
        company = Company.objects.get(id=company_id)
        
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        
        project = Project.objects.create(
            name=project_name,
            description=project_description,
            company=company
        )

        # Create initial features
        feature_names = ['Login System (Authn/Authz systems)', 'Admin Panel']
        for name in feature_names:
            Feature.objects.create(name=name, project=project)
        project.generate_industry_specific_features()
        
        return redirect('game_loop')

class ManageProjectView(View):
    def get(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = Project.objects.get(id=project_id, company=company)
        features = project.features.all()
        detected_bugs = Bug.objects.filter(project=project, state='DETECTED')
        assigned_employees = project.employees.all()

        return render(request, 'game/manage_project.html', {
            'company': company,
            'project': project,
            'features': features,
            'detected_bugs': detected_bugs,
            'assigned_employees': assigned_employees
        })

    def post(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = Project.objects.get(id=project_id, company=company)
        
        # Progress features
        for feature in project.features.all():
            if feature.state == 'NOT_STARTED':
                feature.state = 'IN_PROGRESS'
            elif feature.state == 'IN_PROGRESS':
                if random.random() < 0.3:  # 30% chance to complete a feature
                    feature.state = 'COMPLETED'
            feature.save()

        # Potentially discover bugs
        for bug in project.bugs.filter(state='UNDETECTED'):
            if random.random() < 0.2:  # 20% chance to detect a bug
                bug.state = 'DETECTED'
                bug.save()

        # Potentially create new bugs
        if random.random() < 0.1:  # 10% chance to create a new bug
            Bug.objects.create(
                description=f"New bug in {project.name}",
                project=project,
                state='UNDETECTED'
            )

        return redirect('manage_project', project_id=project_id)

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

class AssignEmployeesView(View):
    def get(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = get_object_or_404(Project, id=project_id, company=company)
        employees = company.employees.filter(project__isnull=True)

        context = {
            'company': company,
            'project': project,
            'employees': employees,
        }
        return render(request, 'game/assign_employees.html', context)

    def post(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = get_object_or_404(Project, id=project_id, company=company)

        selected_employee_ids = request.POST.getlist('employees')
        Employee.objects.filter(id__in=selected_employee_ids).update(project=project)

        return redirect('manage_project', project_id=project_id)

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

        turn_numbers = list(range(0, len(funds_history)))

        # Prepare data for project progress chart
        projects = company.projects.all()
        project_names = [project.name for project in projects]
        completed_features = [project.features.filter(state='COMPLETED').count() for project in projects]
        total_features = [project.features.count() for project in projects]

        # Add a "No projects" entry if there are no projects
        if not projects:
            project_names = ["No projects"]
            completed_features = [0]
            total_features = [0]

        context = {
            'company': company,
            'turn': turn,
            'turn_numbers': json.dumps(turn_numbers),
            'funds_history': json.dumps(funds_history),
            'revenue_history': json.dumps(revenue_history),
            'project_names': json.dumps(project_names),
            'completed_features': json.dumps(completed_features),
            'total_features': json.dumps(total_features),
        }

        return render(request, 'game/dashboard.html', context)