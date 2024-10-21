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
import logging

logger = logging.getLogger(__name__)

class CreateProjectView(View):
    def get(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        form = CreateProjectForm(initial={'industry': company.industry})
        return render(request, 'game/create_project.html', {'company': company, 'form': form})

    def post(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        form = CreateProjectForm(request.POST, initial={'industry': company.industry})
        logger.info(f"Form data: {request.POST}")
        if form.is_valid():
            project = form.save(commit=False)
            project.company = company
            project.save()

            # Create features based on form data
            required_features = form.cleaned_data['required_features']
            optional_features = form.cleaned_data['optional_features']
            for feature_name in required_features + optional_features:
                complexity = form.cleaned_data[f'{feature_name}_complexity']
                logger.info(f"Creating feature {feature_name} with complexity {complexity}")
                Feature.objects.create(
                    name=feature_name,
                    project=project,
                    complexity=complexity,
                    is_required=feature_name in required_features
                )
            
            project.deadline_type = form.cleaned_data['deadline_type']
            project.save()

            return redirect('game_loop')
        else:
            logger.error(f"Form errors: {form.errors}")
        
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
