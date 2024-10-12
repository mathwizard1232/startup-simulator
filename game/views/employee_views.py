from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.employee import Employee
import random
from decimal import Decimal

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

        # Calculate the first week's salary
        weekly_salary = Decimal(salary) / Decimal('52')

        # Check if the company can afford the first week's salary
        if company.funds < weekly_salary:
            return render(request, 'game/hire_employee.html', {
                'company': company,
                'error': "Not enough funds to hire this employee."
            })

        employee = Employee.objects.create(
            name=f"Employee {company.employees.count() + 1}",
            is_perfectionist=is_perfectionist,
            skill_level=skill_level,
            salary=salary,
            company=company
        )

        # Deduct the first week's salary from the company's funds
        company.funds -= weekly_salary
        company.save()

        return redirect('game_loop')