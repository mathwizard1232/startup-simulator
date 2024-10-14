from .company import Company
from .project import Project
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ..name_generator import generate_name
import random

class Employee(models.Model):
    EMPLOYEE_TYPES = [
        ('PERFECTIONIST', 'Perfectionist'),
        ('FAST_WORKER', 'Fast Worker'),
    ]

    name = models.CharField(max_length=100, default=generate_name)
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    # Skill attributes
    coding_speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    coding_accuracy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    debugging = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    teamwork = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )

    def __str__(self):
        return f"{self.name} ({self.get_employee_type_display()})"

    def generate_initial_skills(self):
        if self.employee_type == 'FAST_WORKER':
            self.coding_speed = random.randint(6, 10)
            self.coding_accuracy = random.randint(1, 7)
        else:  # PERFECTIONIST
            self.coding_speed = random.randint(1, 7)
            self.coding_accuracy = random.randint(6, 10)
        
        self.debugging = random.randint(1, 10)
        self.teamwork = random.randint(1, 10)
        self.save()
