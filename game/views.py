from django.shortcuts import render, redirect
from django.views import View
from .models import Company, Employee, Project
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