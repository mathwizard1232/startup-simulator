from .company import Company
from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    is_perfectionist = models.BooleanField(default=False)
    skill_level = models.IntegerField(default=1)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    morale = models.IntegerField(default=100)
    productivity = models.IntegerField(default=100)

    def __str__(self):
        return self.name