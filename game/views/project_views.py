from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from ..models.company import Company
from ..models.project import Project
from ..models.employee import Employee
from ..models.feature import Feature
from ..models.bug import Bug
from ..utils import get_company_or_redirect
from ..forms.project_form import CreateProjectForm
from ..forms.assign_employees_form import AssignEmployeesForm

class CreateProjectView(View):
    def get(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        form = CreateProjectForm()
        return render(request, 'game/create_project.html', {'company': company, 'form': form})

    def post(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.company = company
            project.save()

            # Create initial features
            feature_names = ['Login System (Authn/Authz systems)', 'Admin Panel']
            for name in feature_names:
                Feature.objects.create(name=name, project=project)
            project.generate_industry_specific_features()
            
            return redirect('game_loop')
        
        return render(request, 'game/create_project.html', {'company': company, 'form': form})

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
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        project = get_object_or_404(Project, id=project_id, company=company)
        form = AssignEmployeesForm(company=company, project=project)
        return render(request, 'game/assign_employees.html', {'form': form, 'project': project})

    def post(self, request, project_id):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        project = get_object_or_404(Project, id=project_id, company=company)
        form = AssignEmployeesForm(request.POST, company=company, project=project)
        if form.is_valid():
            assigned_employees = form.cleaned_data['employees']
            project.employees.set(assigned_employees)
            return redirect('manage_project', project_id=project.id)
        
        return render(request, 'game/assign_employees.html', {'form': form, 'project': project})
