from django.shortcuts import render, redirect
from django.views import View
from .models import Company, Employee, Project, Feature, Bug
import random

class StartGameView(View):
    def get(self, request):
        return render(request, 'game/start_game.html')

    def post(self, request):
        company_name = request.POST.get('company_name')
        initial_funds = 100000  # $100,000 initial funding

        company = Company.objects.create(name=company_name, funds=initial_funds)
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
        # Process turn actions here
        # For now, just increment the turn counter
        request.session['turn'] = request.session.get('turn', 1) + 1
        return redirect('game_loop')

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

        company.funds -= salary
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
        feature_names = ['Login System', 'User Profile', 'Main Functionality', 'Admin Panel']
        for name in feature_names:
            Feature.objects.create(name=name, project=project)

        # Generate hidden bugs
        self.generate_hidden_bugs(project)

        return redirect('game_loop')

    def generate_hidden_bugs(self, project):
        num_bugs = random.randint(2, 5)
        for _ in range(num_bugs):
            Bug.objects.create(
                description=f"Hidden bug in {project.name}",
                project=project,
                state='UNDETECTED'
            )

class ManageProjectView(View):
    def get(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = Project.objects.get(id=project_id, company=company)
        features = project.features.all()
        detected_bugs = project.bugs.filter(state='DETECTED')

        return render(request, 'game/manage_project.html', {
            'company': company,
            'project': project,
            'features': features,
            'detected_bugs': detected_bugs
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