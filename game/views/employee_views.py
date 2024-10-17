from django.shortcuts import render, redirect
from django.views import View
from ..models.company import Company
from ..models.employee import Employee
from ..utils import get_company_or_redirect
from ..forms.hire_employee_form import HireEmployeeForm
from decimal import Decimal
from ..name_generator import generate_name
from ..personality_traits import PERSONALITY_TRAITS
import random
import logging
from datetime import timedelta
from ..models.hiringprocess import HiringProcess
from ..views.game_views import GameLoopView
logger = logging.getLogger(__name__)

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
            hiring_process = form.cleaned_data['hiring_process']
            
            # Calculate hire date based on hiring process
            current_date = company.current_date
            if hiring_process == 'resume_only':
                hire_date = current_date
            elif hiring_process == 'phone_interview':
                hire_date = current_date + timedelta(days=1)
            elif hiring_process == 'live_coding':
                hire_date = current_date + timedelta(days=7)
            elif hiring_process == 'full_interview':
                hire_date = current_date + timedelta(days=30)
            
            # Create a hiring process object
            HiringProcess.objects.create(
                company=company,
                employee_type=employee_type,
                process_type=hiring_process,
                start_date=current_date,
                expected_hire_date=hire_date
            )
            logger.info(f"Hiring process created of type: {hiring_process} for {employee_type}")

            # process the immediate hiring if resume_only
            if hiring_process == 'resume_only':
                GameLoopView.process_hiring(company)

            return redirect('game_loop')
        
        return render(request, 'game/hire_employee.html', {'company': company, 'form': form})
