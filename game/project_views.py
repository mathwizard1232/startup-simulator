from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models.company import Company
from .models.project import Project
from .models.employee import Employee
from .models.feature import Feature
from .models.bug import Bug

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
        project = get_object_or_404(Project, id=project_id, company=company)
        features = project.features.all()
        detected_bugs = Bug.objects.filter(project=project, state='DETECTED')
        assigned_employees = project.employees.all()

        return render(request, 'game/manage_project.html', {
            'company': company,
            'project': project,
            'features': features,
            'detected_bugs': detected_bugs,
            'assigned_employees': assigned_employees,
        })

    def post(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = get_object_or_404(Project, id=project_id, company=company)

        action = request.POST.get('action')
        if action == 'add_feature':
            feature_name = request.POST.get('feature_name')
            Feature.objects.create(name=feature_name, project=project)
        elif action == 'fix_bug':
            bug_id = request.POST.get('bug_id')
            bug = get_object_or_404(Bug, id=bug_id, project=project)
            bug.state = 'FIXED'
            bug.save()

        return redirect('manage_project', project_id=project_id)

class AssignEmployeesView(View):
    def get(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = get_object_or_404(Project, id=project_id, company=company)
        employees = company.employees.all()
        assigned_employees = project.employees.all()

        return render(request, 'game/assign_employees.html', {
            'company': company,
            'project': project,
            'employees': employees,
            'assigned_employees': assigned_employees,
        })

    def post(self, request, project_id):
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('start_game')

        company = Company.objects.get(id=company_id)
        project = get_object_or_404(Project, id=project_id, company=company)

        selected_employee_ids = request.POST.getlist('employees')
        project.employees.clear()
        for employee_id in selected_employee_ids:
            employee = get_object_or_404(Employee, id=employee_id, company=company)
            project.employees.add(employee)

        return redirect('manage_project', project_id=project_id)
