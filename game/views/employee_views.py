from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.employee import Employee
from ..utils import get_company_or_redirect
from ..forms.hire_employee_form import HireEmployeeForm
from decimal import Decimal
from ..name_generator import generate_name

class HireEmployeeView(View):
    def get(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        form = HireEmployeeForm()
        return render(request, 'game/hire_employee.html', {'company': company, 'form': form})

    def post(self, request):
        company, redirect_response = get_company_or_redirect(request)
        if redirect_response:
            return redirect_response
        
        form = HireEmployeeForm(request.POST)
        if form.is_valid():
            employee_type = form.cleaned_data['employee_type']
            
            if employee_type == 'PERFECTIONIST':
                salary = Decimal('80000')
            else:  # FAST_WORKER
                salary = Decimal('60000')

            weekly_salary = salary / Decimal('52')  # Calculate weekly salary

            if company.funds < weekly_salary:
                form.add_error(None, "Not enough funds to hire this employee.")
                return render(request, 'game/hire_employee.html', {'company': company, 'form': form})

            employee = Employee.objects.create(
                company=company,
                name=f"{generate_name()} (Employee #{company.employees.count() + 1})",
                employee_type=employee_type,
                salary=salary
            )
            employee.generate_initial_skills()
            company.funds -= weekly_salary
            company.save()

            return redirect('game_loop')
        
        return render(request, 'game/hire_employee.html', {'company': company, 'form': form})
