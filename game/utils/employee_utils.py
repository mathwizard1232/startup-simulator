from decimal import Decimal
import random
from ..models.employee import Employee
from ..models.company import Company
from ..personality_traits import PERSONALITY_TRAITS
from ..models.hiringprocess import HiringProcess
import logging
from ..name_generator import generate_name
logger = logging.getLogger(__name__)

def create_employee(hiring: HiringProcess):
    """
    Create an employee from a hiring process.
    """
    if hiring.employee_type == 'PERFECTIONIST':
        salary = Decimal('80000')
    else:  # FAST_WORKER
        salary = Decimal('60000')

    weekly_salary = salary / Decimal('52')  # Calculate weekly salary

    if hiring.company.funds < weekly_salary:
        logger.info(f"Not enough funds to hire employee {hiring.employee_type}")
        # We are going to allow it go forward; just will make company go bankrupt
        pass

    employee = Employee.objects.create(
        company=hiring.company,
        name=f"{generate_name()} (Employee #{hiring.company.employees.count() + 1})",
        employee_type=hiring.employee_type,
        salary=salary
    )
    # This indicates that the hiring process is complete
    hiring.employee = employee
    hiring.save()
    employee.generate_initial_skills(hiring.process_type)
    hiring.company.funds -= weekly_salary
    # Generate a random set of personality traits for the employee
    num_traits = random.randint(1, 2)
    traits = random.sample(list(PERSONALITY_TRAITS.keys()), num_traits)
    employee.personality_traits_string = ','.join(traits)
    employee.save()
    logger.info(f"Hired employee {employee.name} with {employee.personality_traits} and {employee.coding_speed}, {employee.coding_accuracy}, {employee.debugging}, {employee.teamwork}")
    hiring.company.save()
