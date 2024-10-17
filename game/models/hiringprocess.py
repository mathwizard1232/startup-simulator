from django.db import models
from .company import Company
from .employee import Employee

class HiringProcess(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee_type = models.CharField(max_length=20)
    process_type = models.CharField(max_length=20)
    start_date = models.DateField()
    expected_hire_date = models.DateField()
    employee = models.OneToOneField(Employee, null=True, blank=True, on_delete=models.SET_NULL)

    def is_complete(self):
        return self.employee is not None